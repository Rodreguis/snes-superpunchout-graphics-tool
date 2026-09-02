"""
Super Punch-Out!! (SNES) Graphics Codec
Decompression and compression tool for SNES graphics data

The compression format uses a control byte followed by data:
- Control byte bit 7 = 0: Literal run (copy raw bytes)
- Control byte bit 7 = 1: Repeat run (repeat single byte)
- Control byte bits 0-6: Length - 1
"""

class GraphicsCodec:
    """Handles compression and decompression of Super Punch-Out!! graphics"""
    
    @staticmethod
    def decompress(data: bytes) -> bytes:
        """
        Decompress Super Punch-Out!! graphics data
        
        Args:
            data: Compressed graphics bytes
            
        Returns:
            Decompressed graphics bytes
        """
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("Data must be bytes or bytearray")
        
        output = bytearray()
        pos = 0
        
        while pos < len(data):
            control_byte = data[pos]
            pos += 1
            
            if control_byte & 0x80:  # Repeat run
                count = (control_byte & 0x7F) + 1
                if pos >= len(data):
                    raise ValueError(f"Unexpected end of data at position {pos}")
                value = data[pos]
                pos += 1
                output.extend([value] * count)
            else:  # Literal run
                count = control_byte + 1
                if pos + count > len(data):
                    raise ValueError(f"Unexpected end of data at position {pos}")
                output.extend(data[pos:pos + count])
                pos += count
        
        return bytes(output)
    
    @staticmethod
    def compress(data: bytes) -> bytes:
        """
        Compress graphics data using Super Punch-Out!! format
        
        Args:
            data: Raw graphics bytes to compress
            
        Returns:
            Compressed graphics bytes
        """
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("Data must be bytes or bytearray")
        
        if len(data) == 0:
            return b''
        
        output = bytearray()
        pos = 0
        
        while pos < len(data):
            # Try to find a repeat run
            repeat_length = GraphicsCodec._find_repeat(data, pos)
            
            if repeat_length >= 2:  # Only compress if 2+ bytes
                # Use repeat run encoding
                while repeat_length > 0:
                    chunk_size = min(repeat_length, 128)  # Max 128 bytes per chunk
                    control_byte = 0x80 | (chunk_size - 1)
                    output.append(control_byte)
                    output.append(data[pos])
                    pos += chunk_size
                    repeat_length -= chunk_size
            else:
                # Use literal run encoding
                literal_length = GraphicsCodec._find_literal_run(data, pos)
                while literal_length > 0:
                    chunk_size = min(literal_length, 128)  # Max 128 bytes per chunk
                    control_byte = chunk_size - 1
                    output.append(control_byte)
                    output.extend(data[pos:pos + chunk_size])
                    pos += chunk_size
                    literal_length -= chunk_size
        
        return bytes(output)
    
    @staticmethod
    def _find_repeat(data: bytes, pos: int) -> int:
        """Find length of repeated byte sequence"""
        if pos >= len(data):
            return 0
        
        byte_val = data[pos]
        length = 1
        
        while pos + length < len(data) and data[pos + length] == byte_val and length < 128:
            length += 1
        
        return length
    
    @staticmethod
    def _find_literal_run(data: bytes, pos: int) -> int:
        """Find length of non-repeating sequence"""
        if pos >= len(data):
            return 0
        
        length = 1
        
        while pos + length < len(data) and length < 128:
            # Check if next byte(s) form a repeat
            if GraphicsCodec._find_repeat(data, pos + length) >= 2:
                break
            length += 1
        
        return length
    
    @staticmethod
    def hex_to_bytes(hex_string: str) -> bytes:
        """Convert hex string to bytes"""
        # Remove spaces and common separators
        clean_hex = hex_string.replace(' ', '').replace('\n', '').replace('\r', '')
        
        # Validate hex string
        if len(clean_hex) % 2 != 0:
            raise ValueError("Hex string must have even number of characters")
        
        try:
            return bytes.fromhex(clean_hex)
        except ValueError as e:
            raise ValueError(f"Invalid hex string: {e}")
    
    @staticmethod
    def bytes_to_hex(data: bytes, uppercase: bool = True, line_length: int = 16) -> str:
        """Convert bytes to formatted hex string"""
        fmt = '{:02X}' if uppercase else '{:02x}'
        hex_chars = [fmt.format(b) for b in data]
        
        # Format with line breaks
        lines = []
        for i in range(0, len(hex_chars), line_length):
            lines.append(' '.join(hex_chars[i:i + line_length]))
        
        return '\n'.join(lines)
