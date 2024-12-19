import os
import xml.etree.ElementTree as ET
import secrets
from PIL import Image, ImageOps

xml_path = ""
updated_xml_name = ""
path_to_fronts = ""
path_to_backs = ""
add_boarder = ""

card_slot_mapping = {}

# Sets the DPI of given image
def set_dpi(imagePath, dpi):
    img = Image.open(imagePath)
    img = img.convert('RGB')
    img.save(imagePath, dpi=(dpi, dpi))
    print(f"DPI set to {dpi} for {imagePath}")

# Added Block boarder around images
def add_border(imagePath, borderSize):
    img = Image.open(imagePath)
    img_with_border = Image.new('RGB', (img.width + 2 * borderSize, img.height + 2 * borderSize), 'black')
    img_with_border.paste(img, (borderSize, borderSize))
    img_with_border.save(imagePath)
    print(f"Border added to {imagePath}")

def add_images_to_order(xml_path, image_dir, output_xml):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    fronts = root.find('fronts')
    backs = root.find('backs')
    details = root.find('details')

    # Quantity Tag
    quantity_tag = details.find('quantity')
    initial_quantity = int(quantity_tag.text)

    cards_added_count = 0

    # Get the current maximum slot number
    current_slot = max(int(card.find('slots').text) for card in fronts.findall('card')) + 1

    for image_name  in os.listdir(image_dir):
        if image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Create a new front card element
            card_slot_mapping[image_name] = current_slot

            new_card = ET.SubElement(fronts, 'card')
            new_card_id = f"new_{current_slot}"  # Generate a unique ID
            ET.SubElement(new_card, 'id').text = new_card_id
            ET.SubElement(new_card, 'slots').text = str(current_slot)
            ET.SubElement(new_card, 'name').text = image_name
            ET.SubElement(new_card, 'query').text = os.path.splitext(image_name)[0].replace('_', ' ')

            # if current_slot % 2 == 0: 
            #     back_card = ET.SubElement(backs, 'card')
            #     back_card_id = f"new_back_{current_slot}"
            #     ET.SubElement(back_card, 'id').text = back_card_id
            #     ET.SubElement(back_card, 'slots').text = str(current_slot)
            #     ET.SubElement(back_card, 'name').text = f"Back of {image_name}"
            #     ET.SubElement(back_card, 'query').text = f"back {os.path.splitext(image_name)[0]}"

            current_slot += 1
            cards_added_count += 1

    quantity_tag.text = str(initial_quantity + cards_added_count)

    # Write the updated XML to a new file
    tree.write(output_xml, encoding='unicode')
    print(f"Updated XML saved to {output_xml}")

if __name__ == "__main__":
    xml_path = 'cards.xml'
    image_dir = input("Enter Front Images Folder:")
    output_xml = input("Enter output file name (should include .xml):")
    add_images_to_order(xml_path, image_dir, output_xml)
