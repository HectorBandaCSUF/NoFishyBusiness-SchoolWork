"""
backend/tools/volume.py

Volume Calculator tool for NoFishyBusiness.

Computes aquarium water volume (in US gallons) and the corresponding water
weight (in pounds) from tank dimensions given in inches.

Formulas
--------
- volume_gallons = round((length * width * depth) / 231.0, 2)
  (231 cubic inches = 1 US gallon)
- weight_pounds  = round(volume_gallons * 8.34, 2)
  (fresh water weighs approximately 8.34 lb per US gallon)
"""


def calculate_volume(length: float, width: float, depth: float) -> dict:
    """Calculate aquarium water volume and weight from tank dimensions.

    Args:
        length: Tank length in inches (must be positive).
        width:  Tank width in inches (must be positive).
        depth:  Water depth in inches (must be positive).

    Returns:
        A dict with keys:
          - ``volume_gallons`` (float): Water volume rounded to 2 decimal places.
          - ``weight_pounds``  (float): Water weight rounded to 2 decimal places.
    """
    volume_gallons = round((length * width * depth) / 231.0, 2)
    weight_pounds = round(volume_gallons * 8.34, 2)
    return {"volume_gallons": volume_gallons, "weight_pounds": weight_pounds}
