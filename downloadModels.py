import gdown

destination = "models/model.h5"
url = f"https://drive.google.com/uc?id=1nc_0DXH7FlLt-YITYmEdAMiaZ6QobMJD"
gdown.download(url, destination, quiet=False)

