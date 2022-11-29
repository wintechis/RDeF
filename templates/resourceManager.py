import os


class ResourceManager:
    @staticmethod
    def get_resource_path(chapter_path: str, file_name: str) -> str:
        allowed_ext = {".gif", ".jpg", ".jpeg", ".png"}
        main_resource_path = "resources/"
        story_path = os.path.dirname(chapter_path)
        story_resource_dir = os.path.join(story_path, "resources")
        file_name = file_name.lower()

        if any(map(file_name.endswith, allowed_ext)):
            file_path = ResourceManager._search_resource_folder(
                story_resource_dir, main_resource_path, file_name
            )
        else:
            file_path = ResourceManager._search_resource_with_ext(
                story_resource_dir, main_resource_path, file_name, allowed_ext
            )
        if file_path:
            return file_path

        return ResourceManager._get_dummy_filepath(main_resource_path, file_name)

    @staticmethod
    def _search_resource_folder(
        story_resource_dir, main_resource_path, file_name
    ) -> str:
        for r in [story_resource_dir, main_resource_path]:
            for root, dirs, files in os.walk(r):
                # for ext in self.allowed_ext:
                for name in files:
                    if file_name == name.lower():
                        return os.path.join(root, name)
        return ""

    @staticmethod
    def _search_resource_with_ext(
        story_resource_dir, main_resource_path, file_name, exts
    ) -> str:
        for ext in exts:
            file_path = ResourceManager._search_resource_folder(
                story_resource_dir, main_resource_path, file_name + ext
            )
            if file_path:
                break
        return file_path

    @staticmethod
    def _get_dummy_filepath(main_resource_path, file_name) -> str:
        dummy = os.path.join(main_resource_path, "rdef_dummy.jpg")
        if os.path.isfile(dummy):
            return dummy
        raise Exception(
            f"Resource {file_name} and dummy resource {dummy}(full path) do not exist!"
        )
