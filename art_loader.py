import os
import xml.etree.ElementTree as ET
import secrets
from PIL import Image, ImageOps

xml_path = ""
updated_xml_name = ""
path_to_fronts = ""
add_padding_to_fronts = ""
path_to_backs = ""
add_padding_to_backs = ""

target_dpi = 300
padding_size = 75

card_slot_mapping = {}

xml_tree = None

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

def process_image(folder_path, image_name, add_padding):
    imagePath = os.path.join(folder_path, image_name)
    set_dpi(imagePath, target_dpi)
    if(add_padding):
        add_border(imagePath, padding_size)


def add_front_images_to_order(xml_path, image_dir, output_xml):
    global xml_tree
    xml_tree = ET.parse(xml_path)
    root = xml_tree.getroot()

    fronts = root.find('fronts')
    details = root.find('details')

    # Quantity Tag
    quantity_tag = details.find('quantity')
    initial_quantity = int(quantity_tag.text)

    cards_added_count = 0
    current_slot = max(int(card.find('slots').text) for card in fronts.findall('card')) + 1

    for image_name  in os.listdir(image_dir):
        if image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            
            # Process Images
            process_image(image_dir, image_name, add_padding=(add_padding_to_fronts == "y"))

            # Create a new front card element
            card_slot_mapping[image_name] = current_slot

            new_card = ET.SubElement(fronts, 'card')
            new_card_id = f"new_{current_slot}" 
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
    xml_tree.write(output_xml, encoding='unicode')
    print(f"Updated order saved to {output_xml}")



def add_back_images_to_order(image_dir, output_xml):
    global xml_tree
    root = xml_tree.getroot()
    backs = root.find('backs')

    for image_name in os.listdir(image_dir):
        if image_name.lower().endswith(('.png', '.jpg', '.jpeg')):

            # Generate new name
            name, ext = os.path.splitext(image_name)
            new_image_name = f"{name} (back){ext}"
            new_image_path = os.path.join(image_dir, new_image_name)

            # Rename the file
            original_image_path = os.path.join(image_dir, image_name)
            os.rename(original_image_path, new_image_path)

            # Process Image
            process_image(image_dir, new_image_name, add_padding=(add_padding_to_backs == "y"))

            # Get slot of card back
            if image_name in card_slot_mapping:
                slot = card_slot_mapping[image_name]

                # Add Card back to order
                back_card = ET.SubElement(backs, 'card')
                back_card_id = f"new_back_{slot}"
                ET.SubElement(back_card, 'id').text = back_card_id
                ET.SubElement(back_card, 'slots').text = str(slot)
                ET.SubElement(back_card, 'name').text = new_image_name
                ET.SubElement(back_card, 'query').text = f"back {os.path.splitext(new_image_name)[0]}"

    # Write the updated XML to a new file
    xml_tree.write(output_xml, encoding='unicode')
    print(f"Updated order saved to {output_xml}")


if __name__ == "__main__":
    xml_path = 'cards.xml'
    path_to_fronts = input("Enter path to front images folder:")
    updated_xml_name = input("Enter output file name (should include .xml):")
    add_padding_to_fronts = input("Would you like padding to be added to front images to prevent cutoff (y/n):")

    add_front_images_to_order(xml_path, path_to_fronts, updated_xml_name)

    has_backs = input("Does your order contain cards with custom back sides (y/n):")
    if has_backs == "y":
        path_to_backs = input("Enter path to back iamges folder:")
        add_padding_to_backs = input("Add padding to card backs (y/n):")

        add_back_images_to_order(path_to_backs, updated_xml_name)
    
    
