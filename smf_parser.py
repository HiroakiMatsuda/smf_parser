#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This module provides a class that parse a MIDI file.
# This module has been tested on python ver.2.6.6.
# ver0.140625
# (C) 2014 Matsuda Hiroaki 

import os

def decode(data):
    if isinstance(data, list):

        decode_data = 0
        
        for i, element in enumerate(data):
            decode_data |= element << 8 * (len(data) - i - 1)

        return decode_data

    else:
        raise TypeError

def decode_data_byte(data):
    decode_data = 0
        
    for i, element in enumerate(data):
        decode_data |= (ord(element) & 0x7F) << 7 * (len(data) - i - 1)

    return decode_data

class MidiData():

    def __init__(self):
        self.time = 0
        self.event = ''
        
class Parser():

    def __init__(self, file_path):
        
        file_exists = os.path.exists(file_path)

        if file_exists == True:
            print('MIDI file: %s' %(file_path))

        else:
            raise IOError

        self.midi_file = open(file_path, 'rb')

        self.header_size = 0
        self.file_format = 0
        self.number_of_tracks = 0
        self.division = 0

        # Mode 4
        self.omni_flag = {}

        # Running Status
        self.past_status = 0

        self.read_header_chunk()
        self.parsed_data = [self.read_track_chunk() for i in range(self.number_of_tracks)]
 
    def get_parsed_data(self):
        return self.parsed_data

    def read_header_chunk(self):
        
        event                 = self.midi_file.read(4)
        self.header_size      = decode(map(ord, self.midi_file.read(4)))
        self.file_format      = decode(map(ord, self.midi_file.read(2)))
        self.number_of_tracks = decode(map(ord, self.midi_file.read(2)))
        self.division         = decode(map(ord, self.midi_file.read(2)))

    def search_track_chunk(self):

        while True:
            temp = self.midi_file.read(1)

            if temp == 'M':
                temp = self.midi_file.read(1)

                if temp == 'T':
                    temp = self.midi_file.read(1)

                    if temp == 'r':
                        temp = self.midi_file.read(1)

                        if temp == 'k':
                            return True

            elif temp == '':
                return False

    def decode_track_events(self, track_events):

        data_length = len(track_events)
        data_point = 0

        midi_file_data = []

        while data_point < data_length:

            midi_data = MidiData()
            delta_time = []

            while True:
                temp = track_events[data_point]
                delta_time.append(temp)
                data_point += 1

                if ord(temp) < 0x80:
                    break

            if data_point < data_length:
                
                midi_data, data_point = self.read_midi_event(track_events, data_point)
                midi_data.time = decode_data_byte(delta_time)
                midi_file_data.append(midi_data)

                data_point += 1

        return midi_file_data

    def read_track_chunk(self):

        self.search_track_chunk()

        track_size = decode(map(ord, self.midi_file.read(4)))
        track_events = self.midi_file.read(track_size)

        return self.decode_track_events(track_events)

    def decode_meta_event(self, track_events, data_point):
        data_point += 1
        length = ord(track_events[data_point])

        data = ''

        if length != 0:
            data_point += 1
            data = track_events[data_point:data_point + length]
                
            data_point += length - 1

        return data, data_point

    def read_midi_event(self, track_events, data_point):

        temp = ord(track_events[data_point])

        # Checking Rungning Status
        if temp < 128:
            temp = self.past_status
            data_point -= 1
                
        midi_data = MidiData()
        
        # Note Off
        if (temp >> 4) == 0x08:

            channel = temp ^ 0x80

            data_point += 1
            note_number = ord(track_events[data_point])

            data_point += 1
            velocity = ord(track_events[data_point])

            midi_data.event = 'Note Off'
            midi_data.channel = channel
            midi_data.note_number = note_number
            midi_data.velocity = velocity

        # Note On    
        elif (temp >> 4) == 0x09:

            channel = temp ^ 0x90

            data_point += 1
            note_number = ord(track_events[data_point])

            data_point += 1
            velocity = ord(track_events[data_point])

            midi_data.event = 'Note On'
            midi_data.channel = channel
            midi_data.note_number = note_number
            midi_data.velocity = velocity

        # Polyphonic Key Pressure    
        elif (temp >> 4) == 0x0A:

            channel = temp ^ 0xA0

            data_point += 1
            note_number = ord(track_events[data_point])

            data_point += 1
            pressure = ord(track_events[data_point])

            midi_data.event = 'Polyphonic Key Pressure'
            midi_data.channel = channel
            midi_data.note_number = note_number
            midi_data.pressure = pressure

        # Control Change    
        elif (temp >> 4) == 0x0B:

            channel = temp ^ 0xB0

            data_point += 1
            control_number = ord(track_events[data_point])

            data_point += 1
            value = ord(track_events[data_point])

            number_of_channels = 0

            if control_number == 0x7C:
                self.omni_flag[channel] = False

            # Mode 4
            elif control_number == 0x7E and channel in self.omni_flag and self.omni_flag[channel] == False:
                data_point += 1
                number_of_channels = ord(track_events[data_point])

            midi_data.event = 'Control Change'
            midi_data.channel = channel
            midi_data.control_number = control_number
            midi_data.value = value
            midi_data.number_of_channels = number_of_channels

        # Program Change    
        elif (temp >> 4) == 0x0C:

            channel = temp ^ 0xC0

            data_point += 1
            program = ord(track_events[data_point])

            midi_data.event = 'Program Change'
            midi_data.channel = channel
            midi_data.tone_number = program

        # Channel Pressure    
        elif (temp >> 4) == 0x0D:

            channel = temp ^ 0xD0

            data_point += 1
            pressure = ord(track_events[data_point])

            midi_data.event = 'Channel Pressure'
            midi_data.channel = channel
            midi_data.pressure = pressure
            
        # Pitch Bend
        elif (temp >> 4) == 0x0E:

            channel = temp ^ 0xE0

            data_point += 1
            lower = ord(track_events[data_point])

            data_point += 1
            upper = ord(track_events[data_point])
    
            pitch_bend = decode([lower, upper])

            midi_data.event = 'Pitch Bend'
            midi_data.channel = channel
            midi_data.pitch_bend = pitch_bend

        # SysEx
        elif temp == 0xF0:
            data, data_point = self.decode_meta_event(track_events, data_point)

            midi_data.event = 'SysEx F0'
            midi_data.data = data

        # SysEx
        elif temp == 0xF7:
            data, data_point = self.decode_meta_event(track_events, data_point)

            midi_data.event = 'SysEx F7'
            midi_data.data = data

        # Meta Event
        elif temp == 0xFF:
            data_point += 1
            meta_event = ord(track_events[data_point])

            if meta_event == 0x00:
                data, data_point = self.decode_meta_event(track_events, data_point)

                midi_data.event = 'Sequence Number'
                midi_data.sequence_number = decode(map(ord, data))

            elif meta_event == 0x01:
                data, data_point = self.decode_meta_event(track_events, data_point)

                midi_data.event = 'Text'
                midi_data.text = data

            elif meta_event == 0x02:
                data, data_point = self.decode_meta_event(track_events, data_point)

                midi_data.event = 'Copyright Notice'
                midi_data.copyright_notice = data

            elif meta_event == 0x03:
                data, data_point = self.decode_meta_event(track_events, data_point)

                midi_data.event = 'Sequence Name'
                midi_data.sequence_name = data

            elif meta_event == 0x04:
                data, data_point = self.decode_meta_event(track_events, data_point)

                midi_data.event = 'Instrument Names'
                midi_data.instrument_name = data

            elif meta_event == 0x05:
                data, data_point = self.decode_meta_event(track_events, data_point)

                midi_data.event = 'Lyrics'
                midi_data.lyrics = data

            elif meta_event == 0x06:
                data, data_point = self.decode_meta_event(track_events, data_point)

                midi_data.event = 'Marker'
                midi_data.marker = data

            elif meta_event == 0x07:
                data, data_point = self.decode_meta_event(track_events, data_point)

                midi_data.event = 'Cue Point'
                midi_data.cue_point = data

            elif meta_event == 0x08:
                data, data_point = self.decode_meta_event(track_events, data_point)

                midi_data.event = 'Program Name'
                midi_data.programe_name = data
            
            elif meta_event == 0x09:
                data, data_point = self.decode_meta_event(track_events, data_point)

                midi_data.event = 'Device Name'
                midi_data.device_name = data

            elif meta_event == 0x20:
                data, data_point = self.decode_meta_event(track_events, data_point)

                midi_data.event = 'MIDI Channel Prefix'
                midi_data.midi_channel = ord(data)

            elif meta_event == 0x21:
                data, data_point = self.decode_meta_event(track_events, data_point)

                midi_data.event = 'Port Designation'
                midi_data.port = ord(data)

            elif meta_event == 0x2F:
                data, data_point = self.decode_meta_event(track_events, data_point)

                midi_data.event = 'Track Termination'
            
            elif meta_event == 0x51:
                data, data_point = self.decode_meta_event(track_events, data_point)

                midi_data.event = 'Tempo'
                midi_data.tempo = decode(map(ord, data))

            elif meta_event == 0x54:
                data, data_point = self.decode_meta_event(track_events, data_point)

                midi_data.event = 'SMPTE Offset'
                midi_data.offset = decode(data)

            elif meta_event == 0x58:
                data, data_point = self.decode_meta_event(track_events, data_point)

                molecule = ord(data[0])
                denominator = ord(data[1]) ** 2
                click = ord(data[2])
                notes_per_clocks = ord(data[3])

                midi_data.event = 'Setting Time Signature'
                midi_data.molecule = molecule
                midi_data.denominator = denominator
                midi_data.click = click
                midi_data.notes_per_clocks = notes_per_clocks

            elif meta_event == 0x59:
                data, data_point = self.decode_meta_event(track_events, data_point)

                sf = data[0]
                mi = data[1]

                if sf < 0:
                    sf = str(ord(sf)) + 'flat'

                elif sf == 0:
                    sf = 'C'

                elif sf > 0:
                    sf = str(ord(sf)) + 'sharp'

                if mi == 0:
                    mi = 'major'

                elif mi == 1:
                    mi = 'minor'

                midi_data.event = 'Setting Tone'
                midi_data.sf = sf
                midi_data.mi = mi
                
            elif meta_event == 0x7F:
                data, data_point = self.decode_meta_event(track_events, data_point)

                midi_data.event = 'Sequencer Specific Meta-Event'
                midi_data.data = data

        else:
            midi_data.event = 'Unkown'
            data_point += 1
            data_length = ord(track_events[data_point])
            data_point += data_length
            
        self.past_status = temp
                
        return midi_data, data_point

    def print_header(self):
        print('**************** HEADER **************************')
        print("Header size      : %d" %(self.header_size))
        print("File format      : %d" %(self.file_format))
        print("Number of tracks : %d" %(self.number_of_tracks))
        print("Division         : %d" %(self.division))
        
    def print_midi_data(self):
        print('*************** MIDI DATA ************************')
        for data in midi_file:
            for element in data:
                print('Time: %4d   Event: %s' %(element.time, element.event))

    def get_serialized_midi_data(self):
        parsed_data = self.parsed_data

        track_times = []
        for track_data in parsed_data:
            track_times.append([sum([data.time for data in track_data[:i + 1]]) for i in xrange(len(track_data))])
        
        serialized_midi_data = []
        while True:
                if len(track_times) == 0:
                        break

                min_time_list = min(track_times)
                min_time_list_index = track_times.index(min_time_list)
                
                if min_time_list == []:
                        del parsed_data[min_time_list_index]
                        del track_times[min_time_list_index]
                else:
                        midi_data = parsed_data[min_time_list_index][0]
                        midi_data.time = track_times[min_time_list_index][0]

                        serialized_midi_data.append(midi_data)
                        
                        del parsed_data[min_time_list_index][0]
                        del track_times[min_time_list_index][0]

        return serialized_midi_data
      
    def __del__(self):
        self.midi_file.close()

if __name__=="__main__":

    import sys

    command_line_argument = sys.argv
    midi_file_name = command_line_argument[1]

    midi = Parser(midi_file_name)
    midi.print_header()

    parsed_file_name = command_line_argument[2]
    file = open(parsed_file_name, 'w')
    
    file.writelines("**********************************************\n")
    file.writelines("File Name        : %s\n" %(midi_file_name))
    file.writelines("File Format      : %d\n" %(midi.file_format))
    file.writelines("Number of Tracks : %d\n" %(midi.number_of_tracks))
    file.writelines("Division         : %d\n" %(midi.division))
    file.writelines("***************************************++*****\n")

    parsed_data = midi.get_parsed_data()
    track_number = 0

    for track_data in parsed_data:
        for midi_data in track_data:
            if midi_data.event != "Track Termination":
                file.writelines("Time:%4d Event: %s\n" %(midi_data.time, midi_data.event))

            elif midi_data.event == "Track Termination":
                file.writelines("Time:%4d *** Track %2d ***\n" %(midi_data.time, track_number))
                track_number += 1

    file.close()

    if track_number == midi.number_of_tracks:
        print('Succeed to parse "%s"' %(midi_file_name))
    else:
        print('Failed to parse "%s"' %(midi_file_name))
