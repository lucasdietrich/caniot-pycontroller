# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: model.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='model.proto',
  package='cancontroller.ipc',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0bmodel.proto\x12\x11\x63\x61ncontroller.ipc\"$\n\x08\x44\x65viceId\x12\x0c\n\x04type\x18\x01 \x01(\r\x12\n\n\x02id\x18\x02 \x01(\r\"N\n\rGarageCommand\x12\x10\n\x08\x64\x61tetime\x18\x01 \x01(\t\x12+\n\x07\x63ommand\x18\x02 \x01(\x0e\x32\x1a.cancontroller.ipc.Command\"M\n\x0eGarageResponse\x12\x10\n\x08\x64\x61tetime\x18\x01 \x01(\t\x12)\n\x06status\x18\x04 \x01(\x0e\x32\x19.cancontroller.ipc.Status\"l\n\x10\x41ttributeRequest\x12+\n\x06\x64\x65vice\x18\x02 \x01(\x0b\x32\x1b.cancontroller.ipc.DeviceId\x12\x0b\n\x03key\x18\x03 \x01(\r\x12\r\n\x05value\x18\x04 \x01(\r\x12\x0f\n\x07timeout\x18\x05 \x01(\x02\"\x9e\x01\n\x11\x41ttributeResponse\x12+\n\x06\x64\x65vice\x18\x01 \x01(\x0b\x32\x1b.cancontroller.ipc.DeviceId\x12\x0b\n\x03key\x18\x02 \x01(\r\x12\r\n\x05value\x18\x03 \x01(\r\x12)\n\x06status\x18\x04 \x01(\x0e\x32\x19.cancontroller.ipc.Status\x12\x15\n\rresponse_time\x18\x05 \x01(\x02\"\x07\n\x05\x45mpty\"6\n\x07\x44\x65vices\x12+\n\x06\x64\x65vice\x18\x01 \x03(\x0b\x32\x1b.cancontroller.ipc.DeviceId*&\n\x06Status\x12\x06\n\x02OK\x10\x00\x12\x07\n\x03NOK\x10\x01\x12\x0b\n\x07TIMEOUT\x10\x02*X\n\x07\x43ommand\x12\x17\n\x13\x43OMMAND_UNSPECIFIED\x10\x00\x12\x10\n\x0c\x43OMMAND_LEFT\x10\x01\x12\x11\n\rCOMMAND_RIGHT\x10\x02\x12\x0f\n\x0b\x43OMMAND_ALL\x10\x03\x32\xe7\x02\n\rCanController\x12S\n\nSendGarage\x12 .cancontroller.ipc.GarageCommand\x1a!.cancontroller.ipc.GarageResponse\"\x00\x12\\\n\rReadAttribute\x12#.cancontroller.ipc.AttributeRequest\x1a$.cancontroller.ipc.AttributeResponse\"\x00\x12]\n\x0eWriteAttribute\x12#.cancontroller.ipc.AttributeRequest\x1a$.cancontroller.ipc.AttributeResponse\"\x00\x12\x44\n\nGetDevices\x12\x18.cancontroller.ipc.Empty\x1a\x1a.cancontroller.ipc.Devices\"\x00\x62\x06proto3'
)

_STATUS = _descriptor.EnumDescriptor(
  name='Status',
  full_name='cancontroller.ipc.Status',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='OK', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='NOK', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='TIMEOUT', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=567,
  serialized_end=605,
)
_sym_db.RegisterEnumDescriptor(_STATUS)

Status = enum_type_wrapper.EnumTypeWrapper(_STATUS)
_COMMAND = _descriptor.EnumDescriptor(
  name='Command',
  full_name='cancontroller.ipc.Command',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='COMMAND_UNSPECIFIED', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='COMMAND_LEFT', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='COMMAND_RIGHT', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='COMMAND_ALL', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=607,
  serialized_end=695,
)
_sym_db.RegisterEnumDescriptor(_COMMAND)

Command = enum_type_wrapper.EnumTypeWrapper(_COMMAND)
OK = 0
NOK = 1
TIMEOUT = 2
COMMAND_UNSPECIFIED = 0
COMMAND_LEFT = 1
COMMAND_RIGHT = 2
COMMAND_ALL = 3



_DEVICEID = _descriptor.Descriptor(
  name='DeviceId',
  full_name='cancontroller.ipc.DeviceId',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='cancontroller.ipc.DeviceId.type', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='id', full_name='cancontroller.ipc.DeviceId.id', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=34,
  serialized_end=70,
)


_GARAGECOMMAND = _descriptor.Descriptor(
  name='GarageCommand',
  full_name='cancontroller.ipc.GarageCommand',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='datetime', full_name='cancontroller.ipc.GarageCommand.datetime', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='command', full_name='cancontroller.ipc.GarageCommand.command', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=72,
  serialized_end=150,
)


_GARAGERESPONSE = _descriptor.Descriptor(
  name='GarageResponse',
  full_name='cancontroller.ipc.GarageResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='datetime', full_name='cancontroller.ipc.GarageResponse.datetime', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='status', full_name='cancontroller.ipc.GarageResponse.status', index=1,
      number=4, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=152,
  serialized_end=229,
)


_ATTRIBUTEREQUEST = _descriptor.Descriptor(
  name='AttributeRequest',
  full_name='cancontroller.ipc.AttributeRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='device', full_name='cancontroller.ipc.AttributeRequest.device', index=0,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='key', full_name='cancontroller.ipc.AttributeRequest.key', index=1,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='cancontroller.ipc.AttributeRequest.value', index=2,
      number=4, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='timeout', full_name='cancontroller.ipc.AttributeRequest.timeout', index=3,
      number=5, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=231,
  serialized_end=339,
)


_ATTRIBUTERESPONSE = _descriptor.Descriptor(
  name='AttributeResponse',
  full_name='cancontroller.ipc.AttributeResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='device', full_name='cancontroller.ipc.AttributeResponse.device', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='key', full_name='cancontroller.ipc.AttributeResponse.key', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='cancontroller.ipc.AttributeResponse.value', index=2,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='status', full_name='cancontroller.ipc.AttributeResponse.status', index=3,
      number=4, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='response_time', full_name='cancontroller.ipc.AttributeResponse.response_time', index=4,
      number=5, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=342,
  serialized_end=500,
)


_EMPTY = _descriptor.Descriptor(
  name='Empty',
  full_name='cancontroller.ipc.Empty',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=502,
  serialized_end=509,
)


_DEVICES = _descriptor.Descriptor(
  name='Devices',
  full_name='cancontroller.ipc.Devices',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='device', full_name='cancontroller.ipc.Devices.device', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=511,
  serialized_end=565,
)

_GARAGECOMMAND.fields_by_name['command'].enum_type = _COMMAND
_GARAGERESPONSE.fields_by_name['status'].enum_type = _STATUS
_ATTRIBUTEREQUEST.fields_by_name['device'].message_type = _DEVICEID
_ATTRIBUTERESPONSE.fields_by_name['device'].message_type = _DEVICEID
_ATTRIBUTERESPONSE.fields_by_name['status'].enum_type = _STATUS
_DEVICES.fields_by_name['device'].message_type = _DEVICEID
DESCRIPTOR.message_types_by_name['DeviceId'] = _DEVICEID
DESCRIPTOR.message_types_by_name['GarageCommand'] = _GARAGECOMMAND
DESCRIPTOR.message_types_by_name['GarageResponse'] = _GARAGERESPONSE
DESCRIPTOR.message_types_by_name['AttributeRequest'] = _ATTRIBUTEREQUEST
DESCRIPTOR.message_types_by_name['AttributeResponse'] = _ATTRIBUTERESPONSE
DESCRIPTOR.message_types_by_name['Empty'] = _EMPTY
DESCRIPTOR.message_types_by_name['Devices'] = _DEVICES
DESCRIPTOR.enum_types_by_name['Status'] = _STATUS
DESCRIPTOR.enum_types_by_name['Command'] = _COMMAND
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

DeviceId = _reflection.GeneratedProtocolMessageType('DeviceId', (_message.Message,), {
  'DESCRIPTOR' : _DEVICEID,
  '__module__' : 'model_pb2'
  # @@protoc_insertion_point(class_scope:cancontroller.ipc.DeviceId)
  })
_sym_db.RegisterMessage(DeviceId)

GarageCommand = _reflection.GeneratedProtocolMessageType('GarageCommand', (_message.Message,), {
  'DESCRIPTOR' : _GARAGECOMMAND,
  '__module__' : 'model_pb2'
  # @@protoc_insertion_point(class_scope:cancontroller.ipc.GarageCommand)
  })
_sym_db.RegisterMessage(GarageCommand)

GarageResponse = _reflection.GeneratedProtocolMessageType('GarageResponse', (_message.Message,), {
  'DESCRIPTOR' : _GARAGERESPONSE,
  '__module__' : 'model_pb2'
  # @@protoc_insertion_point(class_scope:cancontroller.ipc.GarageResponse)
  })
_sym_db.RegisterMessage(GarageResponse)

AttributeRequest = _reflection.GeneratedProtocolMessageType('AttributeRequest', (_message.Message,), {
  'DESCRIPTOR' : _ATTRIBUTEREQUEST,
  '__module__' : 'model_pb2'
  # @@protoc_insertion_point(class_scope:cancontroller.ipc.AttributeRequest)
  })
_sym_db.RegisterMessage(AttributeRequest)

AttributeResponse = _reflection.GeneratedProtocolMessageType('AttributeResponse', (_message.Message,), {
  'DESCRIPTOR' : _ATTRIBUTERESPONSE,
  '__module__' : 'model_pb2'
  # @@protoc_insertion_point(class_scope:cancontroller.ipc.AttributeResponse)
  })
_sym_db.RegisterMessage(AttributeResponse)

Empty = _reflection.GeneratedProtocolMessageType('Empty', (_message.Message,), {
  'DESCRIPTOR' : _EMPTY,
  '__module__' : 'model_pb2'
  # @@protoc_insertion_point(class_scope:cancontroller.ipc.Empty)
  })
_sym_db.RegisterMessage(Empty)

Devices = _reflection.GeneratedProtocolMessageType('Devices', (_message.Message,), {
  'DESCRIPTOR' : _DEVICES,
  '__module__' : 'model_pb2'
  # @@protoc_insertion_point(class_scope:cancontroller.ipc.Devices)
  })
_sym_db.RegisterMessage(Devices)



_CANCONTROLLER = _descriptor.ServiceDescriptor(
  name='CanController',
  full_name='cancontroller.ipc.CanController',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=698,
  serialized_end=1057,
  methods=[
  _descriptor.MethodDescriptor(
    name='SendGarage',
    full_name='cancontroller.ipc.CanController.SendGarage',
    index=0,
    containing_service=None,
    input_type=_GARAGECOMMAND,
    output_type=_GARAGERESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='ReadAttribute',
    full_name='cancontroller.ipc.CanController.ReadAttribute',
    index=1,
    containing_service=None,
    input_type=_ATTRIBUTEREQUEST,
    output_type=_ATTRIBUTERESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='WriteAttribute',
    full_name='cancontroller.ipc.CanController.WriteAttribute',
    index=2,
    containing_service=None,
    input_type=_ATTRIBUTEREQUEST,
    output_type=_ATTRIBUTERESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='GetDevices',
    full_name='cancontroller.ipc.CanController.GetDevices',
    index=3,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_DEVICES,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_CANCONTROLLER)

DESCRIPTOR.services_by_name['CanController'] = _CANCONTROLLER

# @@protoc_insertion_point(module_scope)
