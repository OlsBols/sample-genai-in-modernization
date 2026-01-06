import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TextField,
  Switch,
  Select,
  MenuItem,
  FormControl,
  FormControlLabel,
  InputLabel,
  Button,
  Alert,
  CircularProgress,
  Paper
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SaveIcon from '@mui/icons-material/Save';
import RestoreIcon from '@mui/icons-material/Restore';

interface ConfigSetting {
  type: 'boolean' | 'number' | 'select' | 'string';
  default: any;
  label: string;
  description: string;
  options?: string[];
  min?: number;
  max?: number;
  step?: number;
}

interface ConfigGroup {
  label: string;
  description: string;
  settings: Record<string, ConfigSetting>;
}

interface ConfigSchema {
  [groupKey: string]: ConfigGroup;
}

export const ConfigurationEditor: React.FC = () => {
  const [schema, setSchema] = useState<ConfigSchema | null>(null);
  const [config, setConfig] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadConfiguration();
  }, []);

  const loadConfiguration = async () => {
    try {
      const [schemaRes, configRes] = await Promise.all([
        fetch('/api/config/schema'),
        fetch('/api/config')
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
      const response = await fetch('/api/config', {
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
      const response = await fetch('/api/config/reset', { method: 'POST' });
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

  const handleChange = (groupKey: string, settingKey: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      [groupKey]: {
        ...prev[groupKey],
        [settingKey]: value
      }
    }));
  };

  const renderSetting = (groupKey: string, settingKey: string, setting: ConfigSetting) => {
    const value = config[groupKey]?.[settingKey] ?? setting.default;

    switch (setting.type) {
      case 'boolean':
        return (
          <Box>
            <FormControlLabel
              control={
                <Switch
                  checked={value}
                  onChange={(e) => handleChange(groupKey, settingKey, e.target.checked)}
                />
              }
              label={setting.label}
            />
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', ml: 4, mt: -1 }}>
              {setting.description}
            </Typography>
          </Box>
        );

      case 'number':
        return (
          <Box>
            <TextField
              type="number"
              label={setting.label}
              value={value}
              onChange={(e) => handleChange(groupKey, settingKey, parseFloat(e.target.value))}
              inputProps={{
                min: setting.min,
                max: setting.max,
                step: setting.step || 1
              }}
              fullWidth
              size="small"
            />
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
              {setting.description}
            </Typography>
          </Box>
        );

      case 'select':
        return (
          <Box>
            <FormControl fullWidth size="small">
              <InputLabel>{setting.label}</InputLabel>
              <Select
                value={value}
                onChange={(e) => handleChange(groupKey, settingKey, e.target.value)}
                label={setting.label}
              >
                {setting.options?.map(option => (
                  <MenuItem key={option} value={option}>{option}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
              {setting.description}
            </Typography>
          </Box>
        );

      default:
        return (
          <Box>
            <TextField
              label={setting.label}
              value={value}
              onChange={(e) => handleChange(groupKey, settingKey, e.target.value)}
              fullWidth
              size="small"
            />
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
              {setting.description}
            </Typography>
          </Box>
        );
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 1200, margin: '0 auto' }}>
      <Typography variant="h4" gutterBottom>
        Configuration Settings
      </Typography>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Customize business case generation settings. Changes apply to new business cases only.
      </Typography>
      
      {message && (
        <Alert severity={message.type} onClose={() => setMessage(null)} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button 
            variant="contained" 
            onClick={handleSave} 
            disabled={saving}
            startIcon={<SaveIcon />}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
          <Button 
            variant="outlined" 
            onClick={handleReset}
            startIcon={<RestoreIcon />}
          >
            Reset to Defaults
          </Button>
        </Box>
      </Paper>

      {schema && Object.entries(schema).map(([groupKey, group]) => (
        <Accordion key={groupKey} defaultExpanded={groupKey === 'pricing'}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box>
              <Typography variant="h6">{group.label}</Typography>
              <Typography variant="body2" color="text.secondary">
                {group.description}
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {Object.entries(group.settings).map(([settingKey, setting]) => (
                <Box key={settingKey}>
                  {renderSetting(groupKey, settingKey, setting)}
                </Box>
              ))}
            </Box>
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
};
