import os
import json
import rasterio
import urllib.request
import pystac

from datetime import datetime, timezone
from shapely.geometry import Polygon, mapping
from tempfile import TemporaryDirectory
from rasterio.warp import calculate_default_transform, reproject, Resampling



def transform_raster(input_raster, output_raster, src_crs, dst_crs):
    """Reproject the raster from src_crs to dst_crs."""
    with rasterio.open(input_raster) as src:
        # Calculate the transformation matrix, new dimensions, and CRS for the output
        transform, width, height = calculate_default_transform(
            src_crs, dst_crs, src.width, src.height, *src.bounds
        )

        # Prepare the output metadata
        out_meta = src.meta.copy()
        out_meta.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        # Reproject the raster data and write it to the output file
        with rasterio.open(output_raster, 'w', **out_meta) as dst:
            for i in range(1, src.count + 1):  # Loop through all bands
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src_crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest
                )


def get_bbox_and_footprint(raster):
    """Extract bounding box and footprint from a raster file.

    Args:
        raster (str): Path to the raster file.

    Returns:
        tuple: (bbox, footprint) where bbox is a list of coordinates and
               footprint is a GeoJSON-like dictionary.
    """
    with rasterio.open(raster) as r:
        bounds = r.bounds
        bbox = [bounds.left, bounds.bottom, bounds.right, bounds.top]
        footprint = Polygon([
            [bounds.left, bounds.bottom],
            [bounds.left, bounds.top],
            [bounds.right, bounds.top],
            [bounds.right, bounds.bottom]
        ])
        return (bbox, mapping(footprint))


def main():
    # Create temporary directory
    tmp_dir = TemporaryDirectory()
    img_path = os.path.join(tmp_dir.name, 'image.tif')

    # Download sample data from SpaceNet
    print("Downloading sample image...")
    url = ('https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/'
           'sentinel-2-pre-c1-l2a/21/N/YC/2022/12/S2B_T21NYC_20221205T140704_L2A/'
           'TCI.tif'
           )
    urllib.request.urlretrieve(url, img_path)
    print(f"Image saved to: {img_path}")

    # Path for the reprojected raster
    reprojected_path = os.path.join(tmp_dir.name, 'reprojected_image.tif')

    # Transform the raster from EPSG:32621 (WGS84/UTM zone 21N) to EPSG:4326 (WGS84)
    print("\nReprojecting raster to EPSG:4326...")
    transform_raster(img_path, reprojected_path, 'EPSG:32621', 'EPSG:4326')
    print(f"Reprojected image saved to: {reprojected_path}")

    # Extract metadata for the reprojected raster
    bbox, footprint = get_bbox_and_footprint(reprojected_path)
    datetime_utc = datetime.now(tz=timezone.utc)

    # Create STAC catalog
    print("\nCreating STAC catalog...")
    catalog = pystac.Catalog(
        id='tutorial-catalog',
        description='This catalog is a basic demonstration catalog with reprojected raster.'
    )

    # Create STAC item from reprojected raster metadata
    print("Creating STAC item for reprojected raster...")
    item = pystac.Item(
        id='reprojected-image',
        geometry=footprint,
        bbox=bbox,
        datetime=datetime_utc,
        properties={}
    )

    # Add the item to the catalog
    catalog.add_item(item)

    # Add the reprojected image as an asset to the item
    print("Adding asset to STAC item...")
    item.add_asset(
        key='image',
        asset=pystac.Asset(
            href=reprojected_path,
            media_type=pystac.MediaType.GEOTIFF
        )
    )

    # Set up the catalog directory structure
    print("\nSetting up catalog structure...")
    stac_dir = os.path.join(tmp_dir.name, "stac")
    catalog.normalize_hrefs(stac_dir)

    # Save the STAC catalog
    print("Saving self-contained STAC catalog...")
    catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)

    # Make asset paths relative and save again
    print("Making asset paths relative and saving again...")
    catalog.make_all_asset_hrefs_relative()
    catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)

    print("\nCatalog saved successfully!")
    print(f"Catalog location: {catalog.get_self_href()}")
    print(f"Item location: {item.get_self_href()}")

    # Print the catalog JSON for inspection
    print("\nCatalog JSON:")
    with open(catalog.get_self_href()) as f:
        print(json.dumps(json.load(f), indent=2))

    print("\nItem JSON:")
    with open(item.get_self_href()) as f:
        print(json.dumps(json.load(f), indent=2))

    # Keep the temporary directory from being deleted until user input
    input("\nPress Enter to clean up temporary files...")
    tmp_dir.cleanup()


if __name__ == "__main__":
    main()
