SET CLIENT_ENCODING TO UTF8;
SET STANDARD_CONFORMING_STRINGS TO ON;


create or replace function BBox(x integer, y integer, zoom integer)
    RETURNS geometry AS
$BODY$
DECLARE
    max numeric := 6378137 * pi();
    res numeric := max * 2 / 2^zoom;
    bbox geometry;
BEGIN
    return ST_MakeEnvelope(
        -max + (x * res),
        max - (y * res),
        -max + (x * res) + res,
        max - (y * res) - res,
        3857);
END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE;

create or replace function get_height_m(integer, integer) returns integer language plpgsql immutable as $$
begin
    begin
        if $1 is not null then
            return $1*4;
        end if;

        if $2 is not null then
          return $2;
        end if;

        return 1*4;
    end;
end;$$;