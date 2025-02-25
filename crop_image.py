import cv2

# Load the image
DECOUTPUT = r'C:\Users\15142\new\Falcor\Source\Samples\EncodeDecode\decOutputBMP'
folder = f'gallery_480_80' # bedroom_720_40 crytek_sponza_720_80 gallery_480_80
image_path = f'{DECOUTPUT}/{folder}/15.bmp' # 479 523
ours = False if '1080_120' in folder else True
image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Reads image in BGR format

# Define crop location (x, y) (0,0 is top-left corner)
CROP = False
DRAW = True

crop_coords = {'bedroom': (600, 100), 'bistro': (650, 500), 
               'crytek_sponza': (160, 610), 'gallery': (1300, 300)}
x, y = 1300, 300  # 0,0 is top left
CROP_SIZE = 512
x2, y2 = x + CROP_SIZE, y + CROP_SIZE  # 512x512 rectangle

if DRAW:
   scenes = ['bedroom', 'bistro', 'crytek_sponza', 'gallery']
   for scene in scenes:
    image = cv2.imread(f'{DECOUTPUT}/{scene}_reference.bmp', cv2.IMREAD_UNCHANGED)  # Reads image in BGR format
    x, y = crop_coords[scene]  # 0,0 is top left
    x2, y2 = x + CROP_SIZE, y + CROP_SIZE  # 512x512 rectangle
    image = cv2.rectangle(image, (x, y), (x2, y2), (0, 0, 255), thickness=10)
    resized_image = cv2.resize(image, (990, 512), interpolation=cv2.INTER_AREA)
    output_path = f"draw_rectangle_{scene}.jpg"
    cv2.imwrite(output_path, resized_image)

 


# Crop 512x512 patch
x, y = 1300, 300  # 0,0 is top left
if CROP:
    patch = image[y:y+CROP_SIZE, x:x+CROP_SIZE]

    # Save or display the cropped patch
    output_path = f"cropped_{folder}_ours.jpg" if ours else f"cropped_{folder}.jpg"
    cv2.imwrite(output_path, patch)
    # cv2.imshow("Patch", patch)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
