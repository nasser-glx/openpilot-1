import struct
from ctypes import create_string_buffer


def add_tesla_crc(msg, msg_len):
  """Calculate CRC8 using 1D poly, FF start, FF end"""
  crc_lookup = [0x00, 0x1D, 0x3A, 0x27, 0x74, 0x69, 0x4E, 0x53, 0xE8, 0xF5, 0xD2, 0xCF, 0x9C, 0x81, 0xA6, 0xBB, 
0xCD, 0xD0, 0xF7, 0xEA, 0xB9, 0xA4, 0x83, 0x9E, 0x25, 0x38, 0x1F, 0x02, 0x51, 0x4C, 0x6B, 0x76, 
0x87, 0x9A, 0xBD, 0xA0, 0xF3, 0xEE, 0xC9, 0xD4, 0x6F, 0x72, 0x55, 0x48, 0x1B, 0x06, 0x21, 0x3C, 
0x4A, 0x57, 0x70, 0x6D, 0x3E, 0x23, 0x04, 0x19, 0xA2, 0xBF, 0x98, 0x85, 0xD6, 0xCB, 0xEC, 0xF1, 
0x13, 0x0E, 0x29, 0x34, 0x67, 0x7A, 0x5D, 0x40, 0xFB, 0xE6, 0xC1, 0xDC, 0x8F, 0x92, 0xB5, 0xA8, 
0xDE, 0xC3, 0xE4, 0xF9, 0xAA, 0xB7, 0x90, 0x8D, 0x36, 0x2B, 0x0C, 0x11, 0x42, 0x5F, 0x78, 0x65, 
0x94, 0x89, 0xAE, 0xB3, 0xE0, 0xFD, 0xDA, 0xC7, 0x7C, 0x61, 0x46, 0x5B, 0x08, 0x15, 0x32, 0x2F, 
0x59, 0x44, 0x63, 0x7E, 0x2D, 0x30, 0x17, 0x0A, 0xB1, 0xAC, 0x8B, 0x96, 0xC5, 0xD8, 0xFF, 0xE2, 
0x26, 0x3B, 0x1C, 0x01, 0x52, 0x4F, 0x68, 0x75, 0xCE, 0xD3, 0xF4, 0xE9, 0xBA, 0xA7, 0x80, 0x9D, 
0xEB, 0xF6, 0xD1, 0xCC, 0x9F, 0x82, 0xA5, 0xB8, 0x03, 0x1E, 0x39, 0x24, 0x77, 0x6A, 0x4D, 0x50, 
0xA1, 0xBC, 0x9B, 0x86, 0xD5, 0xC8, 0xEF, 0xF2, 0x49, 0x54, 0x73, 0x6E, 0x3D, 0x20, 0x07, 0x1A, 
0x6C, 0x71, 0x56, 0x4B, 0x18, 0x05, 0x22, 0x3F, 0x84, 0x99, 0xBE, 0xA3, 0xF0, 0xED, 0xCA, 0xD7, 
0x35, 0x28, 0x0F, 0x12, 0x41, 0x5C, 0x7B, 0x66, 0xDD, 0xC0, 0xE7, 0xFA, 0xA9, 0xB4, 0x93, 0x8E, 
0xF8, 0xE5, 0xC2, 0xDF, 0x8C, 0x91, 0xB6, 0xAB, 0x10, 0x0D, 0x2A, 0x37, 0x64, 0x79, 0x5E, 0x43, 
0xB2, 0xAF, 0x88, 0x95, 0xC6, 0xDB, 0xFC, 0xE1, 0x5A, 0x47, 0x60, 0x7D, 0x2E, 0x33, 0x14, 0x09, 
0x7F, 0x62, 0x45, 0x58, 0x0B, 0x16, 0x31, 0x2C, 0x97, 0x8A, 0xAD, 0xB0, 0xE3, 0xFE, 0xD9, 0xC4]
  crc = 0xFF
  for x in range(0,msg_len,1):
    crc = crc_lookup[crc ^ ord(msg[x])]
  crc = crc ^ 0xFF 
  return crc


def add_tesla_checksum(msg_id, msg):
 """Calculates the checksum for the data part of the Tesla message"""
 checksum = ((msg_id) & 0xFF) + ((msg_id >> 8) & 0xFF)
 for i in range(0,len(msg),1):
  checksum = (checksum + ord(msg[i])) & 0xFF
 return checksum


def create_steering_control(enabled, apply_steer, idx):
 """Creates a CAN message for the Tesla DBC DAS_steeringControl."""
 msg_id = 0x488
 msg_len = 4
 msg = create_string_buffer(msg_len)
 if enabled == False:
  steering_type = 0
 else:
  steering_type = 1
 type_counter = steering_type << 6
 type_counter += idx
 struct.pack_into('!hB', msg, 0,  apply_steer, type_counter)
 struct.pack_into('B', msg, msg_len-1, add_tesla_checksum(msg_id,msg))
 return [msg_id, 0, msg.raw, 2]


def create_epb_enable_signal(idx):
  """Creates a CAN message to simulate EPB enable message"""
  msg_id = 0x214
  msg_len = 3
  msg = create_string_buffer(msg_len)
  struct.pack_into('BB', msg, 0,  1, idx)
  struct.pack_into('B', msg, msg_len-1, add_tesla_checksum(msg_id,msg))
  return [msg_id, 0, msg.raw, 2]
  

def create_cruise_adjust_msg(spdCtrlLvr_stat, real_steering_wheel_stalk):
  """Creates a CAN message from the cruise control stalk.

  Simluates pressing the cruise control stalk (STW_ACTN_RQ.SpdCtrlLvr_Stat

  It is probably best not to flood these messages so that the real
  stalk works normally.

  Args:
    spdCtrlLvr_stat: Int value of dbc entry STW_ACTN_RQ.SpdCtrlLvr_Stat
      (allowing us to simulate pressing the cruise stalk up or down)
    real_steering_wheel_stalk: Previous STW_ACTN_RQ message sent by the real
      stalk. When sending these artifical messages for cruise control, we want
      to mimic whatever windshield wiper and highbeam settings the car is
      currently sending.
    
  """
  msg_id = 0x045  # 69 in hex, STW_ACTN_RQ
  msg_len = 8
  msg = create_string_buffer(msg_len)
  # Do not send messages that conflict with the driver's actual actions on the
  # steering wheel stalk. To ensure this, only send messages when the last
  # message from the car indicates that the stalk is not being used, and copy
  # all the fields you can from the last message.
  if (real_steering_wheel_stalk
      and real_steering_wheel_stalk['spdCtrlLvr_stat'] == 0):
    fake_stalk = real_steering_wheel_stalk.copy()
    fake_stalk['VSL_Enbl_Rq'] = 1
    fake_stalk['DTR_Dist_Rq'] = 255  # 8 bits of ones in all my observations.
    fake_stalk['spdCtrlLvr_stat'] = spdCtrlLvr_stat
    # message count should be 1 more than the previous.
    # TODO: figure out why mc_stw_actn_rq is a float 
    fake_stalk['MC_STW_ACTN_RQ'] = (int(fake_stalk['MC_STW_ACTN_RQ']) + 1) % 16
    # CRC should initially be 0 before a new one is calculated.
    fake_stalk['CRC_STW_ACTN_RQ'] = 0
    
    # set the first byte, containing cruise control
    struct.pack_into('B', msg, 0,
                     (fake_stalk['spdCtrlLvr_stat']) +
                     (fake_stalk['VSL_Enbl_Rq'] << 6))
    # set the 2nd byte, containing DTR_Dist_Rq
    struct.pack_into('B', msg, 1,  fake_stalk['DTR_Dist_Rq'])
    # Set the 3rd byte, containing turn indicator, highbeams, and wiper wash
    # TODO: why are wipers not int?
    struct.pack_into('B', msg, 2,
                     fake_stalk['TurnIndLvr_Stat'] +
                     (int(round(fake_stalk['HiBmLvr_Stat'])) << 2) +
                     (int(round(fake_stalk['WprWashSw_Psd'])) << 4) +
                     (int(round(fake_stalk['WprWash_R_Sw_Posn_V2'])) << 6)
                    )
    # Set the 7th byte, containing the wipers and message counter.
    struct.pack_into('B', msg, 6,
                     int(round(fake_stalk['WprSw6Posn'])) +
                     (fake_stalk['MC_STW_ACTN_RQ'] << 4))
    
    # Finally, set the CRC for the message. Must be calculated last!
    fake_stalk['CRC_STW_ACTN_RQ'] = add_tesla_crc(msg=msg, msg_len=7)
    struct.pack_into('B', msg, msg_len-1, fake_stalk['CRC_STW_ACTN_RQ'])

    return [msg_id, 0, msg.raw, 0]
  else:
    return None
