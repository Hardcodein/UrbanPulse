# -*- coding: utf-8 -*-
from PIL import Image

import os
import shutil
import argparse


TILES_COUNT_EDGE = 10
TILES_COUNT_OVERLAP = 1


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


def get_original_dem_tiles(dem_dir):
    files = {}
    for filename in os.listdir(dem_dir):
        file, ext = os.path.splitext(filename)

        if ext in ['.tif']:  # '.hgt', '.geotiff'
            files[get_coords_part_from_filename(file)] = file
    return files


def get_coords_part_from_filename(filename):
    arr = filename.strip().lower().split('_')
    assert len(arr) == 3, filename
    name = arr[1]
    sn_title = name[0]
    sn_val = name[1:3]

    ew_title = name[3]
    ew_val = name[4:]

    lat = int(sn_val) if sn_title == "n" else -int(sn_val)
    lon = int(ew_val) if ew_title == "e" else -int(ew_val)

    return f"{sn_title}{lat}{ew_title}{lon}"


def get_tile_group(N, E, count, files):
    tile_group = set()
    for i in range(0, count):
        n = N + i
        for j in range(0, count):
            e = E + j
            filename = f"n{n}e{e}"
            if filename in files:
                tile_group.add(files[filename])

    return tile_group


def prepare_tile_groups(files):
    tile_groups = []

    L = TILES_COUNT_EDGE - TILES_COUNT_OVERLAP
    for N in range(0, 89, L):
        for E in range(0, 181, L):
            tile_group = get_tile_group(N, E, TILES_COUNT_EDGE, files)
            if len(tile_group) > 0:
                tile_groups.append(tile_group)

    return tile_groups


def warp_file(dem_dir, file, adapted, warped):
    filepath_in = os.path.join(dem_dir, file + '.tif')

    file_out = file + '.tif'

    adapted_file = os.path.join(adapted, file_out)
    run_cmd(f'gdal_translate -of GTiff -co "TILED=YES" -a_srs "+proj=latlong '
            f'-a_nodata 0 -r bilinear" {filepath_in} {adapted_file}')

    warped_file = os.path.join(warped, file_out)
    run_cmd(f'gdalwarp -r bilinear -of GTiff -co "TILED=YES" -srcnodata 32767 -t_srs EPSG:3785 -rcs -order 3 '
            f'-tr 15 15 -wt Float32 -ot Float32 -wo SAMPLE_STEPS=50 {adapted_file} {warped_file}')
    run_cmd(f'rm {adapted_file}')


def seed_tms(dir_with_merged_files, merged_files_str, work_dir, min_zoom, max_zoom, i, first_run):
    print("seed tms for ", i, " tile group")

    hillshaded = recreate(work_dir, "hillshaded", first_run)
    colored = recreate(work_dir, "colored", first_run)
    hillshaded_transparent = recreate(work_dir, "hillshaded_transparent", first_run)

    tms_hillshade = recreate(work_dir, "tms_hillshade", first_run)
    tms_hillshade = recreate(tms_hillshade, str(i), True)

    tms_colors = recreate(work_dir, "tms_colors", first_run)
    tms_colors = recreate(tms_colors, str(i), True)

    merged_vrt = os.path.join(dir_with_merged_files, f"merged_{i}.vrt")

    run_cmd(f'gdalbuildvrt -r bilinear -overwrite -o {merged_vrt} {merged_files_str}')

    big_hillshade = os.path.join(hillshaded, f"big_hillshade_{i}.tif")
    big_transparent_hillshade = os.path.join(hillshaded_transparent, f"transparent_hillshade_{i}.tif")

    run_cmd(
        f'gdaldem hillshade -co COMPRESS=LZW -co BIGTIFF=YES -compute_edges {merged_vrt} {big_hillshade}')

    run_cmd(f'gdaldem color-relief -co COMPRESS=LZW -co BIGTIFF=YES {big_hillshade} -alpha '
            f'{os.path.join(work_dir, "shade.ramp")} {big_transparent_hillshade}')

    run_cmd(f"rm {big_hillshade}")

    relief_colored = os.path.join(colored, f"relief_colored_{i}.tif")
    run_cmd(
        f'gdaldem color-relief {merged_vrt} {os.path.join(work_dir, "colors.ramp")} {relief_colored}')

    run_cmd(f"rm {merged_vrt}")

    run_cmd(
        f'gdal2tiles.py -z{min_zoom}-{max_zoom} -r bilinear --processes 4 {big_transparent_hillshade} {tms_hillshade}')

    run_cmd(f"rm {big_transparent_hillshade}")

    run_cmd(
        f'gdal2tiles.py -z{min_zoom}-{max_zoom} -r bilinear --processes 4 {relief_colored} {tms_colors}')

    run_cmd(f"rm {relief_colored}")


def seed_dem_tiles(work_dir, min_zoom, max_zoom):
    dem_dir = os.path.join(work_dir, "dem_full_russia")
    res_dir = os.path.join(work_dir, "dem_intermediate")

    print(f"DEM dir: {dem_dir}. Out dir: {res_dir}. Min zoom = {min_zoom}, max zoom = {max_zoom}")
    dem_files = get_original_dem_tiles(dem_dir)
    tile_groups = prepare_tile_groups(dem_files)

    print(f"Prepared {len(tile_groups)} tile groups.")
    print(f"Tile groups: {tile_groups}")

    adapted = recreate(res_dir, "adapted", first_run=True)
    warped = recreate(res_dir, "warped", first_run=True)
    merged = recreate(res_dir, "merged", first_run=True)

    merged_files_str = ""

    managed_files = set()

    for i, tile_group in enumerate(tile_groups):
        for file in tile_group:
            if file not in managed_files:
                warp_file(dem_dir, file, adapted, warped)
                managed_files.add(file)

            warped_file = os.path.join(warped, file + '.tif')
            merged_files_str += warped_file + " "

        seed_tms(merged, merged_files_str, res_dir, min_zoom, max_zoom, i, i == 0)

        generate_xyz(work_dir, os.path.join(res_dir, "tms_colors", str(i)),
                     os.path.join(res_dir, "tms_hillshade", str(i)), min_zoom, max_zoom)


def generate_xyz(work_dir, tms_colors, tms_hillshade, min_zoom, max_zoom):
    path_jpg = recreate(os.path.join(work_dir, "tiles"), "relief_jpg", first_run=True)
    path_png = recreate(os.path.join(work_dir, "tiles"), "relief_png", first_run=True)

    for zdir in os.listdir(tms_colors):
        try:
            z = int(zdir)
            if z in range(min_zoom, max_zoom+1):
                print("z:", zdir)
                for xdir in os.listdir(os.path.join(tms_colors, zdir)):
                    try:
                        x = int(xdir)
                        os.makedirs(os.path.join(path_png, zdir, xdir))
                        pathx = os.path.join(tms_colors, zdir, xdir)

                        for yfile in os.listdir(pathx):
                            file, ext = os.path.splitext(yfile.lower())

                            if ext == ".png":
                                y_tms = int(file)
                                y_xyz = (2 ** z) - y_tms - 1

                                try:
                                    background = Image.open(os.path.join(tms_colors, zdir, xdir, yfile))
                                    foreground = Image.open(os.path.join(tms_hillshade, zdir, xdir, yfile))
                                    composite_img = Image.alpha_composite(background, foreground)

                                    filepath_out = os.path.join(path_png, zdir, xdir, str(y_xyz) + ".png")
                                    if os.path.exists(filepath_out):
                                        existent_img = Image.alpha_composite(Image.open(filepath_out), composite_img)
                                        existent_img.save(filepath_out, optimize=True, quality=75)
                                    else:
                                        composite_img.save(filepath_out, optimize=True, quality=75)

                                except Exception as e:
                                    print("Exception in PIL", e)
                                    exit()
                    except ValueError as ve:
                        print(ve)
        except ValueError:
            pass


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-d", "--work_dir", type=str, help="Directory with DEM hgt files (SRTM, ASTER, etc)")
    parser.add_argument("-l", "--min_zoom", type=int, help="Min zoom")
    parser.add_argument("-g", "--max_zoom", type=int, help="Max zoom")

    args = parser.parse_args()
    seed_dem_tiles(args.work_dir, args.min_zoom, args.max_zoom)


if __name__ == "__main__":
    main()
