'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Plus, Pencil, Trash2, Settings, Battery, Wifi } from 'lucide-react';
import { GlassCard } from '@/components/layout/glass-card';
import { AnimatedPageWrapper, StaggeredGrid } from '@/components/layout/animated-page-wrapper';
import { GradientText } from '@/components/animations';
import { useStaggerAnimation } from '@/hooks/use-gsap';

interface Device {
  id: string;
  device_id: string;
  name: string;
  device_type: 'TEMP' | 'HUMIDITY' | 'DOOR' | 'PLUG' | 'MOTION';
  status: 'ACTIVE' | 'INACTIVE' | 'LOW_BATTERY' | 'OFFLINE' | 'MAINTENANCE';
  location?: string;
  battery_percent?: number;
  rssi?: number;
  last_seen?: string;
  temp_threshold_min?: number;
  temp_threshold_max?: number;
  reporting_interval: number;
}

interface Location {
  id: string;
  name: string;
}

interface DeviceManagementProps {
  restaurantId: string;
}

export function DeviceManagement({ restaurantId }: DeviceManagementProps) {
  const [devices, setDevices] = useState<Device[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    device_id: '',
    name: '',
    device_type: 'TEMP' as const,
    location: '',
    temp_threshold_min: 33,
    temp_threshold_max: 41,
    reporting_interval: 300,
  });

  useEffect(() => {
    // Load devices (mock data for now)
    const mockDevices: Device[] = [
      {
        id: '1',
        device_id: '0x00158d0001a2b3c4',
        name: 'Walk-in Cooler #1',
        device_type: 'TEMP',
        status: 'ACTIVE',
        location: 'Walk-in Cooler',
        battery_percent: 85,
        rssi: -52,
        last_seen: new Date().toISOString(),
        temp_threshold_min: 33,
        temp_threshold_max: 41,
        reporting_interval: 300,
      },
      {
        id: '2',
        device_id: '0x00158d0002b3c4d5',
        name: 'Walk-in Freezer',
        device_type: 'TEMP',
        status: 'ACTIVE',
        location: 'Walk-in Freezer',
        battery_percent: 92,
        rssi: -48,
        last_seen: new Date().toISOString(),
        temp_threshold_min: -10,
        temp_threshold_max: 0,
        reporting_interval: 300,
      },
      {
        id: '3',
        device_id: '0x00158d0003c4d5e6',
        name: 'Hot Holding Station',
        device_type: 'TEMP',
        status: 'LOW_BATTERY',
        location: 'Kitchen Line',
        battery_percent: 18,
        rssi: -65,
        last_seen: new Date(Date.now() - 300000).toISOString(),
        temp_threshold_min: 135,
        temp_threshold_max: null,
        reporting_interval: 300,
      },
      {
        id: '4',
        device_id: '0x00158d0004d5e6f7',
        name: 'Kitchen Door',
        device_type: 'DOOR',
        status: 'ACTIVE',
        location: 'Kitchen Entrance',
        battery_percent: 78,
        rssi: -55,
        last_seen: new Date().toISOString(),
        reporting_interval: 60,
      },
      {
        id: '5',
        device_id: '0x00158d0005e6f708',
        name: 'Prep Area Humidity',
        device_type: 'HUMIDITY',
        status: 'OFFLINE',
        location: 'Prep Area',
        battery_percent: null,
        rssi: null,
        last_seen: new Date(Date.now() - 7200000).toISOString(),
        reporting_interval: 300,
      },
    ];

    const mockLocations: Location[] = [
      { id: '1', name: 'Walk-in Cooler' },
      { id: '2', name: 'Walk-in Freezer' },
      { id: '3', name: 'Kitchen Line' },
      { id: '4', name: 'Prep Area' },
      { id: '5', name: 'Dining Area' },
      { id: '6', name: 'Dry Storage' },
      { id: '7', name: 'Dishwashing Area' },
    ];

    setDevices(mockDevices);
    setLocations(mockLocations);
    setIsLoading(false);
  }, [restaurantId]);

  const handleAddDevice = () => {
    // Reset form
    setFormData({
      device_id: '',
      name: '',
      device_type: 'TEMP',
      location: '',
      temp_threshold_min: 33,
      temp_threshold_max: 41,
      reporting_interval: 300,
    });
    setIsAddModalOpen(true);
  };

  const handleEditDevice = (device: Device) => {
    setSelectedDevice(device);
    setFormData({
      device_id: device.device_id,
      name: device.name,
      device_type: device.device_type,
      location: device.location || '',
      temp_threshold_min: device.temp_threshold_min ?? 33,
      temp_threshold_max: device.temp_threshold_max ?? 41,
      reporting_interval: device.reporting_interval,
    });
    setIsEditModalOpen(true);
  };

  const handleDeleteDevice = (deviceId: string) => {
    if (confirm('Are you sure you want to delete this device?')) {
      setDevices(devices.filter(d => d.id !== deviceId));
      // TODO: Call API to delete device
    }
  };

  const handleSaveDevice = () => {
    if (isEditModalOpen && selectedDevice) {
      // Edit existing device
      setDevices(devices.map(d =>
        d.id === selectedDevice.id
          ? { ...d, ...formData }
          : d
      ));
    } else {
      // Add new device
      const newDevice: Device = {
        id: Date.now().toString(),
        ...formData,
        status: 'ACTIVE',
        battery_percent: 100,
        rssi: -50,
        last_seen: new Date().toISOString(),
      };
      setDevices([...devices, newDevice]);
    }

    setIsAddModalOpen(false);
    setIsEditModalOpen(false);
    setSelectedDevice(null);

    // TODO: Call API to save device
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      ACTIVE: { variant: 'success' as const, label: 'Active', pulse: false },
      INACTIVE: { variant: 'secondary' as const, label: 'Inactive', pulse: false },
      LOW_BATTERY: { variant: 'warning' as const, label: 'Low Battery', pulse: true },
      OFFLINE: { variant: 'critical' as const, label: 'Offline', pulse: true },
      MAINTENANCE: { variant: 'default' as const, label: 'Maintenance', pulse: false },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.ACTIVE;
    return <Badge variant={config.variant} pulse={config.pulse}>{config.label}</Badge>;
  };

  const getDeviceTypeBadge = (type: string) => {
    const typeConfig = {
      TEMP: { variant: 'default' as const, label: 'Temperature' },
      HUMIDITY: { variant: 'glass' as const, label: 'Humidity' },
      DOOR: { variant: 'secondary' as const, label: 'Door' },
      PLUG: { variant: 'outline' as const, label: 'Smart Plug' },
      MOTION: { variant: 'default' as const, label: 'Motion' },
    };

    const config = typeConfig[type as keyof typeof typeConfig] || typeConfig.TEMP;
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Device Management</h2>
        </div>
        <div className="text-muted-foreground">Loading devices...</div>
      </div>
    );
  }

  return (
    <AnimatedPageWrapper animation="fade" className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold">
            <GradientText variant="primary">Device Management</GradientText>
          </h2>
          <p className="text-muted-foreground mt-1">
            Manage sensors and IoT devices for this restaurant
          </p>
        </div>
        <Button onClick={handleAddDevice} variant="gradient" className="gap-2">
          <Plus className="h-4 w-4" />
          Add Device
        </Button>
      </div>

      {/* Summary Cards */}
      <StaggeredGrid cols={4}>
        <GlassCard>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Devices</p>
                <p className="text-3xl font-bold">{devices.length}</p>
              </div>
              <Settings className="h-10 w-10 text-muted-foreground opacity-50" />
            </div>
          </CardContent>
        </GlassCard>
        <GlassCard>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active</p>
                <p className="text-3xl font-bold text-emerald-600">
                  {devices.filter(d => d.status === 'ACTIVE').length}
                </p>
              </div>
            </div>
          </CardContent>
        </GlassCard>
        <GlassCard>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Offline</p>
                <p className="text-3xl font-bold text-rose-600">
                  {devices.filter(d => d.status === 'OFFLINE').length}
                </p>
              </div>
              <Wifi className="h-10 w-10 text-rose-500 opacity-50" />
            </div>
          </CardContent>
        </GlassCard>
        <GlassCard>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Low Battery</p>
                <p className="text-3xl font-bold text-amber-600">
                  {devices.filter(d => d.status === 'LOW_BATTERY').length}
                </p>
              </div>
              <Battery className="h-10 w-10 text-amber-500 opacity-50" />
            </div>
          </CardContent>
        </GlassCard>
      </StaggeredGrid>

      {/* Device List */}
      <GlassCard>
        <CardHeader>
          <CardTitle>All Devices</CardTitle>
          <CardDescription>
            View and manage all registered sensors and devices
          </CardDescription>
        </CardHeader>
        <CardContent>
          {devices.length === 0 ? (
            <div className="text-center py-12">
              <Settings className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-muted-foreground mb-4">No devices registered yet</p>
              <Button onClick={handleAddDevice}>
                <Plus className="h-4 w-4 mr-2" />
                Add Your First Device
              </Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Device</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Battery</TableHead>
                    <TableHead>Signal</TableHead>
                    <TableHead>Last Seen</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {devices.map((device, index) => (
                    <TableRow
                      key={device.id}
                      className="hover:bg-muted/50 transition-all duration-300 hover:scale-[1.01] hover:shadow-md stagger-item"
                      style={{ animationDelay: `${index * 0.05}s` }}
                    >
                      <TableCell className="font-medium">
                        {device.name}
                        <div className="text-xs text-muted-foreground mt-1">
                          ID: {device.device_id}
                        </div>
                      </TableCell>
                      <TableCell>{getDeviceTypeBadge(device.device_type)}</TableCell>
                      <TableCell>{device.location || '-'}</TableCell>
                      <TableCell>{getStatusBadge(device.status)}</TableCell>
                      <TableCell>
                        {device.battery_percent !== null ? (
                          <div className="flex items-center gap-2">
                            <Battery className={`h-4 w-4 ${
                              device.battery_percent < 20 ? 'text-red-500' :
                              device.battery_percent < 50 ? 'text-yellow-500' :
                              'text-green-500'
                            }`} />
                            <span className="text-sm font-medium">{device.battery_percent}%</span>
                          </div>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {device.rssi !== null ? (
                          <div className="flex items-center gap-2">
                            <Wifi className={`h-4 w-4 ${
                              device.rssi > -60 ? 'text-green-500' :
                              device.rssi > -75 ? 'text-yellow-500' :
                              'text-red-500'
                            }`} />
                            <span className="text-xs text-muted-foreground">{device.rssi} dBm</span>
                          </div>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {new Date(device.last_seen || '').toLocaleString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEditDevice(device)}
                            className="hover:scale-110 transition-transform"
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteDevice(device.id)}
                            className="text-destructive hover:text-destructive hover:scale-110 transition-transform"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </GlassCard>

      {/* Add Device Modal */}
      <Dialog open={isAddModalOpen} onOpenChange={setIsAddModalOpen}>
        <DialogContent className="sm:max-w-[600px] glass-card">
          <DialogHeader>
            <DialogTitle>Add New Device</DialogTitle>
            <DialogDescription>
              Register a new IoT sensor or device to your restaurant
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            {/* Device ID */}
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="device_id" className="text-right">
                Device ID
              </Label>
              <Input
                id="device_id"
                placeholder="0x00158d0001a2b3c4"
                value={formData.device_id}
                onChange={(e) => setFormData({ ...formData, device_id: e.target.value })}
                className="col-span-3"
                required
              />
            </div>

            {/* Device Name */}
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">
                Name
              </Label>
              <Input
                id="name"
                placeholder="Walk-in Cooler #1"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="col-span-3"
                required
              />
            </div>

            {/* Device Type */}
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="device_type" className="text-right">
                Type
              </Label>
              <Select
                value={formData.device_type}
                onValueChange={(value) => setFormData({ ...formData, device_type: value as any })}
                className="col-span-3"
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="TEMP">🌡️ Temperature Sensor</SelectItem>
                  <SelectItem value="HUMIDITY">💧 Humidity Sensor</SelectItem>
                  <SelectItem value="DOOR">🚪 Door Sensor</SelectItem>
                  <SelectItem value="PLUG">🔌 Smart Plug</SelectItem>
                  <SelectItem value="MOTION">🚶 Motion Sensor</SelectItem>
                </SelectContent>
              </Select>

              {/* Location */}
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="location" className="text-right">
                  Location
                </Label>
                <Select
                  value={formData.location}
                  onValueChange={(value) => setFormData({ ...formData, location: value })}
                  className="col-span-3"
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select location" />
                  </SelectTrigger>
                  <SelectContent>
                    {locations.map((loc) => (
                      <SelectItem key={loc.id} value={loc.name}>
                        {loc.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                {/* Temperature Thresholds (for TEMP type) */}
                {formData.device_type === 'TEMP' && (
                  <>
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="temp_threshold_min" className="text-right">
                        Min Temp (°F)
                      </Label>
                      <Input
                        id="temp_threshold_min"
                        type="number"
                        step="0.1"
                        value={formData.temp_threshold_min}
                        onChange={(e) => setFormData({ ...formData, temp_threshold_min: parseFloat(e.target.value) })}
                        className="col-span-3"
                      />
                    </div>

                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="temp_threshold_max" className="text-right">
                        Max Temp (°F)
                      </Label>
                      <Input
                        id="temp_threshold_max"
                        type="number"
                        step="0.1"
                        value={formData.temp_threshold_max}
                        onChange={(e) => setFormData({ ...formData, temp_threshold_max: parseFloat(e.target.value) })}
                        className="col-span-3"
                      />
                    </div>
                  </>
                )}

                {/* Reporting Interval */}
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="reporting_interval" className="text-right">
                    Interval (seconds)
                  </Label>
                  <Input
                    id="reporting_interval"
                    type="number"
                    value={formData.reporting_interval}
                    onChange={(e) => setFormData({ ...formData, reporting_interval: parseInt(e.target.value) })}
                    className="col-span-3"
                  />
                  <p className="col-span-4 text-xs text-muted-foreground">
                    How often the sensor sends readings (300 = 5 minutes)
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsAddModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveDevice}>
              Add Device
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Edit Device Modal */}
      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent className="sm:max-w-[600px] glass-card">
          <DialogHeader>
            <DialogTitle>Edit Device</DialogTitle>
            <DialogDescription>
              Update device configuration and settings
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit_name" className="text-right">
                Name
              </Label>
              <Input
                id="edit_name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="col-span-3"
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit_location" className="text-right">
                Location
              </Label>
              <Select
                value={formData.location}
                onValueChange={(value) => setFormData({ ...formData, location: value })}
                className="col-span-3"
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {locations.map((loc) => (
                    <SelectItem key={loc.id} value={loc.name}>
                      {loc.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {formData.device_type === 'TEMP' && (
              <>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="edit_temp_min" className="text-right">
                    Min Temp (°F)
                  </Label>
                  <Input
                    id="edit_temp_min"
                    type="number"
                    step="0.1"
                    value={formData.temp_threshold_min}
                    onChange={(e) => setFormData({ ...formData, temp_threshold_min: parseFloat(e.target.value) })}
                    className="col-span-3"
                  />
                </div>

                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="edit_temp_max" className="text-right">
                    Max Temp (°F)
                  </Label>
                  <Input
                    id="edit_temp_max"
                    type="number"
                    step="0.1"
                    value={formData.temp_threshold_max}
                    onChange={(e) => setFormData({ ...formData, temp_threshold_max: parseFloat(e.target.value) })}
                    className="col-span-3"
                  />
                </div>
              </>
            )}

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit_interval" className="text-right">
                Interval (seconds)
              </Label>
              <Input
                id="edit_interval"
                type="number"
                value={formData.reporting_interval}
                onChange={(e) => setFormData({ ...formData, reporting_interval: parseInt(e.target.value) })}
                className="col-span-3"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsEditModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveDevice} variant="gradient">
              Save Changes
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </AnimatedPageWrapper>
  );
}
