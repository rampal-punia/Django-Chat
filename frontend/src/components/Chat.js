// src/components/Chat.js

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TextField, Button, List, ListItem, ListItemText, Typography } from '@material-ui/core';

const Chat = () => {
    const [conversations, setConversations] = useState([]);
    const [selectedConversation, setSelectedConversation] = useState(null);
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');

    useEffect(() => {
        fetchConversations();
    }, []);

    const fetchConversations = async () => {
        try {
            const response = await axios.get('/api/conversations/');
            setConversations(response.data);
        } catch (error) {
            console.error('Error fetching conversations:', error);
        }
    };

    const fetchMessages = async (conversationId) => {
        try {
            const response = await axios.get(`/api/messages/?conversation=${conversationId}`);
            setMessages(response.data);
        } catch (error) {
            console.error('Error fetching messages:', error);
        }
    };

    const handleConversationSelect = (conversation) => {
        setSelectedConversation(conversation);
        fetchMessages(conversation.id);
    };

    const handleSendMessage = async () => {
        try {
            await axios.post('/api/messages/', {
                conversation: selectedConversation.id,
                content: newMessage,
                is_from_user: true
            });
            setNewMessage('');
            fetchMessages(selectedConversation.id);
        } catch (error) {
            console.error('Error sending message:', error);
        }
    };

    return (
        <div>
            <Typography variant="h4">Chat</Typography>
            <div style={{ display: 'flex' }}>
                <List style={{ width: '30%' }}>
                    {conversations.map((conversation) => (
                        <ListItem
                            button
                            key={conversation.id}
                            onClick={() => handleConversationSelect(conversation)}
                        >
                            <ListItemText primary={conversation.title} />
                        </ListItem>
                    ))}
                </List>
                <div style={{ width: '70%' }}>
                    {selectedConversation && (
                        <>
                            <List>
                                {messages.map((message) => (
                                    <ListItem key={message.id}>
                                        <ListItemText
                                            primary={message.content}
                                            secondary={message.is_from_user ? 'You' : 'AI'}
                                        />
                                    </ListItem>
                                ))}
                            </List>
                            <TextField
                                value={newMessage}
                                onChange={(e) => setNewMessage(e.target.value)}
                                fullWidth
                                variant="outlined"
                            />
                            <Button onClick={handleSendMessage} variant="contained" color="primary">
                                Send
                            </Button>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Chat;