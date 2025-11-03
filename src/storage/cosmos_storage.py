"""Cosmos DB storage implementation for conversations."""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)


class CosmosConversationStorage:
    """Stores conversation history in Azure Cosmos DB."""

    def __init__(self):
        """Initialize Cosmos DB client and container."""
        self.endpoint = os.getenv("AZURE_COSMOS_ENDPOINT")
        self.key = os.getenv("AZURE_COSMOS_KEY")
        self.database_name = os.getenv("AZURE_COSMOS_DATABASE", "AgentDB")
        self.container_name = os.getenv("AZURE_COSMOS_CONTAINER", "conversations")
        
        if not self.endpoint:
            raise ValueError("AZURE_COSMOS_ENDPOINT environment variable is required")
        
        # Initialize client - use key if provided, otherwise use managed identity
        if self.key:
            logger.info("Initializing Cosmos DB client with API key")
            self.client = CosmosClient(self.endpoint, credential=self.key)
        else:
            logger.info("Initializing Cosmos DB client with Managed Identity")
            credential = DefaultAzureCredential()
            self.client = CosmosClient(self.endpoint, credential=credential)
        
        # Get database and container
        self.database = self.client.get_database_client(self.database_name)
        self.container = self.database.get_container_client(self.container_name)
        
        logger.info(f"Cosmos DB storage initialized: {self.database_name}/{self.container_name}")

    async def save_message(self, session_id: str, role: str, content: str) -> None:
        """Save a conversation message to Cosmos DB.
        
        Args:
            session_id: Unique session identifier
            role: Message role (user, assistant, system)
            content: Message content
        """
        try:
            # Try to get existing conversation
            conversation = self._get_conversation(session_id)
            
            # Add new message
            conversation["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Update last modified
            conversation["lastModified"] = datetime.utcnow().isoformat()
            
            # Upsert the conversation
            self.container.upsert_item(conversation)
            logger.info(f"Saved message for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error saving message to Cosmos DB: {e}")
            raise

    async def get_conversation(self, session_id: str) -> List[Dict]:
        """Retrieve conversation history from Cosmos DB.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            List of conversation messages
        """
        try:
            conversation = self._get_conversation(session_id)
            return conversation.get("messages", [])
        except CosmosResourceNotFoundError:
            logger.info(f"No conversation found for session {session_id}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving conversation from Cosmos DB: {e}")
            return []

    async def delete_conversation(self, session_id: str) -> bool:
        """Delete a conversation from Cosmos DB.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            self.container.delete_item(item=session_id, partition_key=session_id)
            logger.info(f"Deleted conversation for session {session_id}")
            return True
        except CosmosResourceNotFoundError:
            logger.warning(f"Conversation {session_id} not found for deletion")
            return False
        except Exception as e:
            logger.error(f"Error deleting conversation from Cosmos DB: {e}")
            return False

    async def get_all_sessions(self) -> List[str]:
        """Get all active session IDs.
        
        Returns:
            List of session IDs
        """
        try:
            query = "SELECT c.sessionId FROM c"
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            return [item["sessionId"] for item in items]
        except Exception as e:
            logger.error(f"Error retrieving sessions from Cosmos DB: {e}")
            return []

    def _get_conversation(self, session_id: str) -> Dict:
        """Get conversation document or create new one.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Conversation document
        """
        try:
            # Try to read existing conversation
            return self.container.read_item(item=session_id, partition_key=session_id)
        except CosmosResourceNotFoundError:
            # Create new conversation document
            return {
                "id": session_id,
                "sessionId": session_id,
                "messages": [],
                "created": datetime.utcnow().isoformat(),
                "lastModified": datetime.utcnow().isoformat()
            }
