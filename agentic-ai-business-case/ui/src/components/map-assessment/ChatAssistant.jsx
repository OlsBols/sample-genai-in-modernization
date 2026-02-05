import React, { useState, useRef, useEffect } from 'react';
import {
  Container,
  Header,
  SpaceBetween,
  Input,
  Button,
  Alert,
  Box,
  Spinner
} from '@cloudscape-design/components';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { getApiUrl } from '../../utils/apiConfig.js';

function ChatAssistant() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(getApiUrl('/map/chat/message'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: inputMessage,
          history: messages,
          context: {}
        })
      });

      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.message);
      }

      const assistantMessage = {
        role: 'assistant',
        content: result.response,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(err.message || 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  return (
    <SpaceBetween size="l">
      <Container
        header={
          <Header
            variant="h1"
            description="Context-Aware Conversations with Generated Outputs"
            actions={
              <Button onClick={clearChat} disabled={messages.length === 0}>
                Clear Chat
              </Button>
            }
          >
            Interactive Analysis Chat
          </Header>
        }
      >
        <SpaceBetween size="m">
          <Alert type="info">
            Ask questions about your migration analysis, explore scenarios, and get 
            context-aware recommendations based on your generated outputs.
          </Alert>

          {error && (
            <Alert
              type="error"
              dismissible
              onDismiss={() => setError(null)}
            >
              {error}
            </Alert>
          )}

          <div
            style={{
              minHeight: '400px',
              maxHeight: '600px',
              overflowY: 'auto',
              backgroundColor: '#f9f9f9',
              borderRadius: '8px',
              border: '1px solid #e0e0e0',
              padding: '16px'
            }}
          >
            {messages.length === 0 ? (
              <Box textAlign="center" padding="xxl" color="text-body-secondary">
                <Box variant="p" fontSize="heading-m">
                  👋 Welcome to the MAP Assessment Chat
                </Box>
                <Box variant="p" padding={{ top: 's' }}>
                  Start a conversation by asking questions about AWS migration, 
                  modernization strategies, or any analysis you've generated.
                </Box>
              </Box>
            ) : (
              <SpaceBetween size="m">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    style={{
                      backgroundColor: message.role === 'user' ? '#e8f4f8' : 'white',
                      borderRadius: '8px',
                      border: '1px solid #e0e0e0',
                      marginLeft: message.role === 'user' ? '20%' : '0',
                      marginRight: message.role === 'assistant' ? '20%' : '0',
                      padding: '12px'
                    }}
                  >
                    <SpaceBetween size="xs">
                      <Box variant="strong" color={message.role === 'user' ? 'text-status-info' : 'text-status-success'}>
                        {message.role === 'user' ? '👤 You' : '🤖 Assistant'}
                      </Box>
                      <div className="markdown-content">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {message.content}
                        </ReactMarkdown>
                      </div>
                      <Box variant="small" color="text-body-secondary">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </Box>
                    </SpaceBetween>
                  </div>
                ))}
                {loading && (
                  <Box textAlign="center" padding="m">
                    <Spinner size="large" />
                    <Box variant="p" padding={{ top: 's' }}>
                      Assistant is thinking...
                    </Box>
                  </Box>
                )}
                <div ref={messagesEndRef} />
              </SpaceBetween>
            )}
          </div>

          <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
            <div style={{ flex: 1 }}>
              <Input
                value={inputMessage}
                onChange={({ detail }) => setInputMessage(detail.value)}
                onKeyDown={handleKeyPress}
                placeholder="Type your message here... (Press Enter to send)"
                disabled={loading}
              />
            </div>
            <Button
              variant="primary"
              onClick={handleSendMessage}
              disabled={loading || !inputMessage.trim()}
              iconName="send"
            >
              Send
            </Button>
          </div>
        </SpaceBetween>
      </Container>
    </SpaceBetween>
  );
}

export default ChatAssistant;
