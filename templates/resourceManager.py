import os

class ResourceManager:
    @staticmethod
    def get_resource_path(chapter_path: str, file_name: str) -> str:
        allowed_ext = {'.png', '.jpg'}
        main_resource_path = 'resources/'
        story_path = os.path.dirname(chapter_path)
        story_resource_dir = os.path.join(story_path, 'resources')
        file_name = file_name.lower()
        for r in [story_resource_dir, main_resource_path]:
            for root, dirs, files in os.walk(r):
                #for ext in self.allowed_ext:
                for name in files:
                    if file_name == name.lower():
                        return os.path.join(root, name)
        dummy = os.path.join(main_resource_path, 'rdef_dummy.jpg')
        if os.path.isfile(dummy): return dummy
        raise Exception(f'Resource {file_name} and dummy resource {dummy}(full path) do not exist!')