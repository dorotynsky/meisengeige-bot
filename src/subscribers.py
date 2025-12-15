"""Subscriber management for Telegram notifications."""

import json
from pathlib import Path
from typing import Set, Optional


class SubscriberManager:
    """Manages the list of subscribers for notifications."""

    def __init__(self, storage_file: str = "state/subscribers.json"):
        """
        Initialize subscriber manager.

        Args:
            storage_file: Path to JSON file storing subscribers
        """
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(exist_ok=True)
        self._subscribers: Set[int] = self._load_subscribers()

    def _load_subscribers(self) -> Set[int]:
        """
        Load subscribers from storage file.

        Returns:
            Set of subscriber chat IDs
        """
        if not self.storage_file.exists():
            return set()

        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('subscribers', []))
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error loading subscribers: {e}")
            return set()

    def _save_subscribers(self) -> None:
        """Save subscribers to storage file."""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(
                    {'subscribers': list(self._subscribers)},
                    f,
                    ensure_ascii=False,
                    indent=2
                )
        except OSError as e:
            print(f"Error saving subscribers: {e}")

    def add_subscriber(self, chat_id: int) -> bool:
        """
        Add a new subscriber.

        Args:
            chat_id: Telegram chat ID to add

        Returns:
            True if subscriber was added, False if already exists
        """
        if chat_id in self._subscribers:
            return False

        self._subscribers.add(chat_id)
        self._save_subscribers()
        return True

    def remove_subscriber(self, chat_id: int) -> bool:
        """
        Remove a subscriber.

        Args:
            chat_id: Telegram chat ID to remove

        Returns:
            True if subscriber was removed, False if not found
        """
        if chat_id not in self._subscribers:
            return False

        self._subscribers.remove(chat_id)
        self._save_subscribers()
        return True

    def is_subscribed(self, chat_id: int) -> bool:
        """
        Check if a chat ID is subscribed.

        Args:
            chat_id: Telegram chat ID to check

        Returns:
            True if subscribed
        """
        return chat_id in self._subscribers

    def get_all_subscribers(self) -> Set[int]:
        """
        Get all subscriber chat IDs.

        Returns:
            Set of chat IDs
        """
        return self._subscribers.copy()

    def get_subscriber_count(self) -> int:
        """
        Get the number of subscribers.

        Returns:
            Number of subscribers
        """
        return len(self._subscribers)
