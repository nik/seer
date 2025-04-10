import os


def dump_code(
    repo_dir=".",
    ignore_dirs=None,
    output_file="combined_code_dump.txt",
    file_extensions=None,
):
    if ignore_dirs is None:
        ignore_dirs = ["node_modules", "dev-dist"]
    if file_extensions is None:
        file_extensions = ["py", "ts", "typed", "tsx"]

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as out:
        for root, dirs, files in os.walk(repo_dir):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                if any(file.endswith(f".{ext}") for ext in file_extensions):
                    file_path = os.path.join(root, file)
                    out.write(f"// File: {file_path}\n")
                    with open(file_path, "r") as f:
                        out.write(f.read())
                    out.write("\n\n")

    print(f"All code files have been combined into {output_file}")
