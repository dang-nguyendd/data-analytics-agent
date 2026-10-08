from pathlib import Path
from datetime import datetime


class ChatStorage:

    def __init__(self, chat_directory="chats"):
        self.chat_directory = Path(chat_directory)
        self.chat_directory.mkdir(parents=True, exist_ok=True)

    # ============================================================
    # Chat listing
    # ============================================================

    def get_chats(self):
        chats = []

        for path in self.chat_directory.glob("*.txt"):
            chats.append({
                "id": path.stem,
                "path": path,
                "title": self.get_title(path),
                "created": self.get_metadata(path, "CREATED"),
                "updated": self.get_metadata(path, "UPDATED"),
                "title_custom": self.is_title_custom(path),
                "modified": path.stat().st_mtime,
            })

        chats.sort(
            key=lambda x: x["modified"],
            reverse=True
        )

        return chats

    # ============================================================
    # Metadata
    # ============================================================

    def get_metadata(self, path, key):
        try:
            with open(path, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()

                    if line.startswith(f"{key}:"):
                        return line.split(":", 1)[1].strip()

        except Exception:
            pass

        return ""

    def get_title(self, path):
        title = self.get_metadata(path, "TITLE")

        if title:
            return title

        return path.stem

    def is_title_custom(self, path):
        value = self.get_metadata(path, "TITLE_CUSTOM")

        return value.lower() in ("1", "true", "yes")

    # ============================================================
    # Create chat
    # ============================================================

    def create_chat(self, title="New Chat"):
        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        chat_id = f"chat_{timestamp}"

        path = self.chat_directory / f"{chat_id}.txt"

        now = datetime.now().isoformat()

        with open(path, "w", encoding="utf-8") as file:
            file.write(f"TITLE: {title}\n")
            file.write(f"TITLE_CUSTOM: 0\n")
            file.write(f"CREATED: {now}\n")
            file.write(f"UPDATED: {now}\n")
            file.write("\n")

        return chat_id

    # ============================================================
    # Save chat
    # ============================================================

    def save_chat(self, chat_id, messages):
        path = self.chat_directory / f"{chat_id}.txt"

        now = datetime.now().isoformat()

        # --------------------------------------------------------
        # Preserve creation time
        # --------------------------------------------------------

        created = self.get_metadata(
            path,
            "CREATED"
        )

        if not created:
            created = now

        # --------------------------------------------------------
        # Check whether title was manually renamed
        # --------------------------------------------------------

        title_custom = self.is_title_custom(path)

        if title_custom:
            # Keep existing manually renamed title
            title = self.get_title(path)

        else:
            # Automatically use first user message
            title = "New Chat"

            for message in messages:
                if message["role"] == "user":
                    title = message["content"].strip()

                    if title:
                        break

        # --------------------------------------------------------
        # Write file
        # --------------------------------------------------------

        with open(path, "w", encoding="utf-8") as file:

            file.write(f"TITLE: {title}\n")
            file.write(
                f"TITLE_CUSTOM: "
                f"{1 if title_custom else 0}\n"
            )
            file.write(f"CREATED: {created}\n")
            file.write(f"UPDATED: {now}\n")
            file.write("\n")

            for message in messages:

                role = message["role"]
                content = message["content"]

                file.write(
                    f"[{role.upper()}]\n"
                )

                file.write(content)
                file.write("\n\n")

    # ============================================================
    # Rename chat
    # ============================================================

    def rename_chat(self, chat_id, new_title):
        path = self.chat_directory / f"{chat_id}.txt"

        if not path.exists():
            return False

        try:
            with open(path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            found_title = False
            found_custom = False

            for i, line in enumerate(lines):

                if line.startswith("TITLE:"):
                    lines[i] = f"TITLE: {new_title}\n"
                    found_title = True

                elif line.startswith("TITLE_CUSTOM:"):
                    lines[i] = "TITLE_CUSTOM: 1\n"
                    found_custom = True

            if not found_title:
                lines.insert(
                    0,
                    f"TITLE: {new_title}\n"
                )

            if not found_custom:
                lines.insert(
                    1,
                    "TITLE_CUSTOM: 1\n"
                )

            with open(path, "w", encoding="utf-8") as file:
                file.writelines(lines)

            return True

        except Exception:
            return False

    # ============================================================
    # Load chat
    # ============================================================

    def load_chat(self, chat_id):
        path = self.chat_directory / f"{chat_id}.txt"

        if not path.exists():
            return None

        messages = []

        current_role = None
        current_content = []

        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        for line in lines:

            stripped = line.strip()

            # Ignore metadata
            if stripped.startswith("TITLE:"):
                continue

            if stripped.startswith("TITLE_CUSTOM:"):
                continue

            if stripped.startswith("CREATED:"):
                continue

            if stripped.startswith("UPDATED:"):
                continue

            # ----------------------------------------------------
            # User message
            # ----------------------------------------------------

            if stripped == "[USER]":

                if current_role is not None:
                    messages.append({
                        "role": current_role,
                        "content": "".join(
                            current_content
                        ).strip()
                    })

                current_role = "user"
                current_content = []

                continue

            # ----------------------------------------------------
            # Assistant message
            # ----------------------------------------------------

            if stripped == "[ASSISTANT]":

                if current_role is not None:
                    messages.append({
                        "role": current_role,
                        "content": "".join(
                            current_content
                        ).strip()
                    })

                current_role = "assistant"
                current_content = []

                continue

            # ----------------------------------------------------
            # Message content
            # ----------------------------------------------------

            if current_role is not None:
                current_content.append(line)

        # Save final message
        if current_role is not None:
            messages.append({
                "role": current_role,
                "content": "".join(
                    current_content
                ).strip()
            })

        return {
            "id": chat_id,
            "title": self.get_title(path),
            "created": self.get_metadata(
                path,
                "CREATED"
            ),
            "updated": self.get_metadata(
                path,
                "UPDATED"
            ),
            "title_custom": self.is_title_custom(path),
            "messages": messages,
        }

    # ============================================================
    # Delete chat
    # ============================================================

    def delete_chat(self, chat_id):
        path = self.chat_directory / f"{chat_id}.txt"

        if path.exists():
            path.unlink()
            return True

        return False