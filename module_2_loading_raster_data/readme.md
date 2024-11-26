# loading raster data

# Learning objectives:
- Create a new python environment
- Create a new STAC catalog
- Loading raster data to STAC
- Creating a STAC collection
- Reprojecting raster data
- Adding the reprojected raster data to the collection


# Lab 2 instructions:

## Part 1: STAC Catalog Tutorial

This tutorial walks through creating a basic SpatioTemporal Asset Catalog (STAC) using PySTAC. The example uses a sample satellite image from the SpaceNet 5 Challenge dataset.

## Prerequisites

- Python 3.7 or higher
- Windows OS (instructions can be adapted for other operating systems)
- Basic familiarity with command line operations

## Setup Instructions

### 1. Create Project Directory and Virtual Environment

Open Command Prompt and run the following commands:

```bash
# Create and enter project directory
md stac_tutorial
cd stac_tutorial

# Create and activate virtual environment
python -m venv venv_name
venv_name\Scripts\activate
```

### 2. Install Required Packages

With the virtual environment activated, install the necessary packages:

```bash
pip install pystac rasterio shapely
```

## Project Structure

Create a new Python script named `stac_demo.py` in your project directory. The final structure will look like:

```
stac_tutorial/
├── venv/
└── stac_demo.py
```

When the script runs, it will create a temporary directory with:

```
tmp_dir/
├── image.tif
└── stac/
    ├── catalog.json
    └── local-image/
        └── local-image.json
```

## Complete Script

Here's the full `stac_demo.py` script with detailed comments:

```python
import os
import json
import rasterio
import urllib.request
import pystac

from datetime import datetime, timezone
from shapely.geometry import Polygon, mapping
from tempfile import TemporaryDirectory

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
    url = ('https://spacenet-dataset.s3.amazonaws.com/'
           'spacenet/SN5_roads/train/AOI_7_Moscow/MS/'
           'SN5_roads_train_AOI_7_Moscow_MS_chip996.tif')
    urllib.request.urlretrieve(url, img_path)
    print(f"Image saved to: {img_path}")

    # Create basic STAC catalog
    print("\nCreating STAC catalog...")
    catalog = pystac.Catalog(
        id='tutorial-catalog',
        description='This catalog is a basic demonstration catalog utilizing a scene from SpaceNet 5.'
    )

    # Extract image metadata
    print("Extracting image metadata...")
    bbox, footprint = get_bbox_and_footprint(img_path)
    datetime_utc = datetime.now(tz=timezone.utc)

    # Create STAC item from metadata
    print("Creating STAC item...")
    item = pystac.Item(
        id='local-image',
        geometry=footprint,
        bbox=bbox,
        datetime=datetime_utc,
        properties={}
    )

    # Add the item to the catalog
    catalog.add_item(item)

    # Add the image as an asset to the item
    print("Adding asset to item...")
    item.add_asset(
        key='image',
        asset=pystac.Asset(
            href=img_path,
            media_type=pystac.MediaType.GEOTIFF
        )
    )

    # Set up the catalog directory structure
    print("\nSetting up catalog structure...")
    stac_dir = os.path.join(tmp_dir.name, "stac")
    catalog.normalize_hrefs(stac_dir)

    # Save as self-contained catalog
    print("Saving self-contained catalog...")
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
```

## Running the Tutorial

1. Save the script above as `stac_demo.py`
2. Ensure your virtual environment is activated
3. Run the script:
   ```bash
   python stac_demo.py
   ```
4. You can also run the script from your preferred IDE.

## Script Output

The script will show progress messages for:
- Image download status
- Catalog creation
- Metadata extraction
- Item and asset addition
- Final JSON structure of both catalog and item

The temporary directory will be maintained until you press Enter, allowing you to inspect the generated files.

## Key Concepts

### STAC Components
- **Catalog**: The root container that holds items and other catalogs
- **Item**: Represents a single asset or set of related assets
- **Asset**: The actual data file (in this case, a satellite image)

### File Organization
- The catalog uses a self-contained format with relative paths
- Assets are linked to items using relative paths
- The directory structure follows STAC best practices

## Troubleshooting

Common issues and solutions:

1. **Package Installation Errors**
   - Ensure you have Python 3.7 or higher
   - Check that your virtual environment is activated
   - Try updating pip: `python -m pip install --upgrade pip`

2. **File Permission Errors**
   - Run Command Prompt as administrator
   - Check write permissions in your project directory

3. **Image Download Issues**
   - Verify your internet connection
   - Check if the SpaceNet URL is accessible
   - Ensure enough disk space for downloads

## Part 2: Load your own data:

You have been given a link to a new image file that you need to load to STAC:
1. Create a new STAC collection for this image called 'sentinel-2-l2a'. Use this tutorial as a guide. "https://stacspec.org/en/tutorials/4-create-stac-collection/"
2. Modify the python script to load data from this link: 'https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-pre-c1-l2a/21/N/YC/2022/12/S2B_T21NYC_20221205T140704_L2A/TCI.tif'
3. This image is in EPSG:32621 (WGS 84 / UTM zone 21N). You will need to reproject it to EPSG:4326 (WGS 84)
3. Add the image to the collection


## Additional Resources

- [PySTAC Documentation Creating a Catalog](https://stacspec.org/en/tutorials/2-create-stac-catalog-python/)
- [PySTAC Documentation Creating a Collection](https://stacspec.org/en/tutorials/4-create-stac-collection/)

# Assessment:

Copy the python script you created for transforming/loading the new image inside the assessment folder.

Take a screenshot of the "bbox" & "assets" portion of theJSON from the output of the second python script where you loaded the new image and save it inside the assessment folder.

Commit and push your changes to the repository.