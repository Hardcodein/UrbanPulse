# -*- coding: utf-8 -*-
from PIL import Image

import os
import shutil
import argparse

EXT_IN = ".png"
EXT_OUT = ".jpg"

THREADS_COUNT = 2


def run_cmd(cmd_str, exit_on_error=True):
    ret_res = os.system(cmd_str)
    if ret_res == 0:
        return 0

    print(f"( ╯°□°)╯ ┻━━┻ ERROR {ret_res} running {cmd_str}")
    if exit_on_error:
        exit()


def recreate(parent_dir, cur_dir, first_run):
    d = os.path.join(parent_dir, cur_dir)
    if first_run:
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
    return d


def split_tile_name(filename):
    arr = filename.strip().lower().split('_')
    if len(arr) == 3:
        name = arr[1] # ASTGTMV003_N55E037_dem.tif
    else:
        name = arr[0] # N45E038.hgt
    sn_title = name[0]

    sn_val = name[1:3]

    ew_title = name[3]
    ew_val = name[4:]

    lat = int(sn_val) if sn_title == "n" else -int(sn_val)
    lon = int(ew_val) if ew_title == "e" else -int(ew_val)

    return [lat, lon]


def are_neighbours(coord1, coord2):
    if abs(coord1[0] - coord2[0]) <= 1 and abs(coord1[1] - coord2[1]) <= 1:
        return True
    return False


def generate_tms_tiles(dir_with_merged_files, merged_files_str, work_folder, min_zoom, max_zoom, i, first_run):
    hillshaded = recreate(work_folder, "hillshaded", first_run)
    colored = recreate(work_folder, "colored", first_run)
    hillshaded_transparent = recreate(work_folder, "hillshaded_transparent", first_run)

    tms_hillshade = recreate(work_folder, "tms_hillshade", first_run)
    tms_colors = recreate(work_folder, "tms_colors", first_run)

    merged_vrt = os.path.join(dir_with_merged_files, f"merged_{i}.vrt")

    run_cmd(f'gdalbuildvrt -r bilinear -overwrite -o {merged_vrt} {merged_files_str}')

    big_hillshade = os.path.join(hillshaded, f"big_hillshade_{i}.tif")
    big_transparent_hillshade = os.path.join(hillshaded_transparent, f"transparent_hillshade_{i}.tif")

    run_cmd(
        f'gdaldem hillshade -co COMPRESS=LZW -co BIGTIFF=YES -compute_edges {merged_vrt} {big_hillshade}')

    run_cmd(f'gdaldem color-relief -co COMPRESS=LZW -co BIGTIFF=YES {big_hillshade} -alpha '
            f'{os.path.join(work_folder, "shade.ramp")} {big_transparent_hillshade}')

    run_cmd(f"rm {big_hillshade}")

    relief_colored = os.path.join(colored, f"relief_colored_{i}.tif")
    run_cmd(
        f'gdaldem color-relief {merged_vrt} {os.path.join(work_folder, "colors.ramp")} {relief_colored}')

    run_cmd(f"rm {merged_vrt}")

    run_cmd(
        f'gdal2tiles.py -z{min_zoom}-{max_zoom} -r bilinear --processes 6 {big_transparent_hillshade} {tms_hillshade}')

    run_cmd(f"rm {big_transparent_hillshade}")

    run_cmd(
        f'gdal2tiles.py -z{min_zoom}-{max_zoom} -r bilinear --processes 6 {relief_colored} {tms_colors}')

    run_cmd(f"rm {relief_colored}")


def get_original_dem_tiles(dem_folder):
    files = []
    for filename in os.listdir(dem_folder):
        file, ext = os.path.splitext(filename)

        if ext in ['.tif', '.hgt']:  # '.hgt', '.geotiff'
            files.append(file)
    return files


def warp_file(dem_folder, file, adapted, warped):
    filepath_in = os.path.join(dem_folder, file + '.hgt')

    file_out = file + '.tif'

    adapted_file = os.path.join(adapted, file_out)
    run_cmd(f'gdal_translate -of GTiff -co "TILED=YES" -a_srs "+proj=latlong '
            f'-a_nodata 0 -r bilinear" {filepath_in} {adapted_file}')

    warped_file = os.path.join(warped, file_out)
    run_cmd(f'gdalwarp -r bilinear -of GTiff -co "TILED=YES" -srcnodata 32767 -t_srs EPSG:3785 -rcs -order 3 '
            f'-tr 15 15 -wt Float32 -ot Float32 -wo SAMPLE_STEPS=50 {adapted_file} {warped_file}')
    run_cmd(f'rm {adapted_file}')


def generate_tms(work_dir, min_zoom, max_zoom):
    dem_folder = os.path.join(work_dir, "dem")
    work_folder = os.path.join(work_dir, "dem_intermediate")

    print(f"In dir: {dem_folder}. Out dir: {work_folder}. Min zoom = {min_zoom}, max zoom = {max_zoom}")

    adapted = recreate(work_folder, "adapted", first_run=True)
    warped = recreate(work_folder, "warped", first_run=True)
    merged = recreate(work_folder, "merged", first_run=True)

    merged_files = []
    files = get_original_dem_tiles(dem_folder)
    files.sort()

    print(f"{len(files)} DEM tiles found for conversion.")
    for file in files:
        warp_file(dem_folder, file, adapted, warped)

    print(f"{len(files)} DEM tiles are converted. Started clustering.")

    for file in files:
        warped_file = os.path.join(warped, file + '.tif')
        merged_files_str = warped_file + " "
        latlon = split_tile_name(file)

        if len(merged_files) == 0:
            merged_files.append([[latlon], merged_files_str])
        else:
            has_neighbour = False

            for i in range(0, len(merged_files)):
                coords, merged_str = merged_files[i]
                for coord in coords:
                    if are_neighbours(coord, latlon):
                        has_neighbour = True
                        merged_files[i][0].append(latlon)
                        merged_files[i][1] += merged_files_str
                        break
                if has_neighbour:
                    break

            if not has_neighbour:
                merged_files.append([[latlon], merged_files_str])

    print(f"WARPED ALL FILES AND PREPARED {len(merged_files)} FILEGROUPS FOR MERGE.")

    for i in range(0, len(merged_files)):
        print(f"Converting {i+1} tile group of {len(merged_files)}")

        merged_files_str = merged_files[i][1]
        generate_tms_tiles(merged, merged_files_str, work_folder, min_zoom, max_zoom, i, i == 0)


def update_img_background(image, image_format):
    img = image.convert(image_format)

    data = img.getdata()

    new_image_data = []
    for item in data:
        # change all black pixels to beige (map background):
        if item[0] == 0 and item[1] == 0 and item[2] == 0:
            if image_format == "RGB":
                new_image_data.append((248, 249, 250))
                continue
            elif image_format == "RGBA" and item[3] == 255:
                new_image_data.append((248, 249, 250, 0))
                continue

        new_image_data.append(item)

    img.putdata(new_image_data)
    return img


def generate_xyz(working_dir, tms_colors, tms_hillshade, res_dir, min_zoom, max_zoom):
    xyz = recreate(os.path.join(working_dir, "tiles"), res_dir, first_run=True)

    for zdir in os.listdir(tms_colors):
        try:
            z = int(zdir)
            if z in range(min_zoom, max_zoom+1):
                print("z:", zdir)
                for xdir in os.listdir(os.path.join(tms_colors, zdir)):
                    try:
                        x = int(xdir)
                        os.makedirs(os.path.join(xyz, zdir, xdir))
                        pathx = os.path.join(tms_colors, zdir, xdir)

                        for yfile in os.listdir(pathx):
                            file, ext = os.path.splitext(yfile.lower())

                            if ext == EXT_IN:
                                y_tms = int(file)
                                y_xyz = (2 ** z) - y_tms - 1

                                try:
                                    background = update_img_background(Image.open(os.path.join(tms_colors, zdir, xdir, yfile)), "RGB")
                                    foreground = update_img_background(Image.open(os.path.join(tms_hillshade, zdir, xdir, yfile)), "RGBA")

                                    filename_out = str(y_xyz) + EXT_OUT

                                    res_img = Image.alpha_composite(background.convert('RGBA'), foreground.convert('RGBA'))

                                    res_img.convert('RGB').save(
                                        os.path.join(xyz, zdir, xdir, filename_out),
                                        optimize=True,
                                        quality=75)

                                except Exception as e:
                                    print("Exception in PIL", e)
                                    exit()
                    except ValueError as ve:
                        print(ve)
        except ValueError:
            pass


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-d", "--working_dir", type=str, help="Directory with DEM hgt files (SRTM, ASTER, etc)")
    parser.add_argument("-l", "--min_zoom", type=int, help="Min zoom")
    parser.add_argument("-g", "--max_zoom", type=int, help="Max zoom")

    args = parser.parse_args()

    generate_tms(args.working_dir, args.min_zoom, args.max_zoom)
    print("GENERATED TMS")
    intermediate_dir = os.path.join(args.working_dir, "dem_intermediate")
    tms_hillshade = os.path.join(intermediate_dir, "tms_hillshade")
    tms_colors = os.path.join(intermediate_dir, "tms_colors")
    generate_xyz(args.working_dir, tms_colors, tms_hillshade, "relief", args.min_zoom, args.max_zoom)


if __name__ == "__main__":
    main()
