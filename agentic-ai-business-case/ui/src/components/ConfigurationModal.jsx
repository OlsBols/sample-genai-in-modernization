import React, { useState, useEffect } from 'react';
import {
  Modal,
  Box,
  SpaceBetween,
  Button,
  Alert,
  Spinner,
  ExpandableSection,
  FormField,
  Toggle,
  Input,
  Select,
  Header
} from '@cloudscape-design/components';

export default function ConfigurationModal({ visible, onDismiss }) {
  const [schema, setSchema] = useState(null);
  const [config, setConfig] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    if (visible) {
      loadConfiguration();
    }
  }, [visible]);

  const loadConfiguration = async () => {
    try {
      const [schemaRes, configRes] = await Promise.all([
        fetch('http://localhost:5000/api/config/schema'),
        fetch('http://localhost:5000/api/config')
      ]);
      
      if (!schemaRes.ok || !configRes.ok) {
        throw new Error('Failed to load configuration');
      }
      
      const schemaData = await schemaRes.json();
      const configData = await configRes.json();
      
      setSchema(schemaData);
      setConfig(configData);
      setLoading(false);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load configuration' });
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const response = await fetch('http://localhost:5000/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      
      if (response.ok) {
        setMessage({ type: 'success', text: 'Configuration saved successfully. Changes will apply to new business cases.' });
      } else {
        throw new Error('Failed to save configuration');
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save configuration' });
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    if (!window.confirm('Reset all settings to defaults? This cannot be undone.')) return;
    
    setMessage(null);
    try {
      const response = await fetch('http://localhost:5000/api/config/reset', { method: 'POST' });
      if (response.ok) {
        await loadConfiguration();
        setMessage({ type: 'success', text: 'Configuration reset to defaults' });
      } else {
        throw new Error('Failed to reset configuration');
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to reset configuration' });
    }
  };

  const handleChange = (groupKey, settingKey, value) => {
    setConfig(prev => ({
      ...prev,
      [groupKey]: {
        ...prev[groupKey],
        [settingKey]: value
      }
    }));
  };

  const renderSetting = (groupKey, settingKey, setting) => {
    const value = config[groupKey]?.[settingKey] ?? setting.default;

    switch (setting.type) {
      case 'boolean':
        return (
          <FormField
            label={setting.label}
            description={setting.description}
          >
            <Toggle
              checked={value}
              onChange={({ detail }) => handleChange(groupKey, settingKey, detail.checked)}
            />
          </FormField>
        );

      case 'number':
        return (
          <FormField
            label={setting.label}
            description={setting.description}
          >
            <Input
              type="number"
              value={String(value)}
              onChange={({ detail }) => handleChange(groupKey, settingKey, parseFloat(detail.value))}
              inputMode="decimal"
              step={setting.step || 1}
            />
          </FormField>
        );

      case 'select':
        return (
          <FormField
            label={setting.label}
            description={setting.description}
          >
            <Select
              selectedOption={{ label: value, value: value }}
              onChange={({ detail }) => handleChange(groupKey, settingKey, detail.selectedOption.value)}
              options={setting.options?.map(opt => ({ label: opt, value: opt })) || []}
            />
          </FormField>
        );

      default:
        return (
          <FormField
            label={setting.label}
            description={setting.description}
          >
            <Input
              value={value}
              onChange={({ detail }) => handleChange(groupKey, settingKey, detail.value)}
            />
          </FormField>
        );
    }
  };

  return (
    <Modal
      visible={visible}
      onDismiss={onDismiss}
      header="Configuration Settings"
      size="large"
      footer={
        <Box float="right">
          <SpaceBetween direction="horizontal" size="xs">
            <Button variant="link" onClick={onDismiss}>Cancel</Button>
            <Button onClick={handleReset}>Reset to Defaults</Button>
            <Button variant="primary" onClick={handleSave} loading={saving}>
              Save Changes
            </Button>
          </SpaceBetween>
        </Box>
      }
    >
      {loading ? (
        <Box textAlign="center" padding="xxl">
          <Spinner size="large" />
        </Box>
      ) : (
        <SpaceBetween size="l">
          {message && (
            <Alert
              type={message.type}
              dismissible
              onDismiss={() => setMessage(null)}
            >
              {message.text}
            </Alert>
          )}

          <Alert type="info">
            Customize business case generation settings. Changes apply to new business cases only.
          </Alert>

          {schema && Object.entries(schema).map(([groupKey, group]) => (
            <ExpandableSection
              key={groupKey}
              headerText={group.label}
              headerDescription={group.description}
              defaultExpanded={groupKey === 'pricing'}
            >
              <SpaceBetween size="m">
                {Object.entries(group.settings).map(([settingKey, setting]) => (
                  <div key={settingKey}>
                    {renderSetting(groupKey, settingKey, setting)}
                  </div>
                ))}
              </SpaceBetween>
            </ExpandableSection>
          ))}
        </SpaceBetween>
      )}
    </Modal>
  );
}
