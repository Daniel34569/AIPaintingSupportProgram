
def read_tags_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        tags = [tag.strip() for tag in content.split(',')]
    return tags

def write_tags_to_file(file_path, tags):
    with open(file_path, 'w') as file:
        content = ', '.join(tags)
        file.write(content)

def save_tags(tags_dict):
    for image_data in tags_dict.values():
        write_tags_to_file(image_data['tagging_file_path'], image_data['tags'])