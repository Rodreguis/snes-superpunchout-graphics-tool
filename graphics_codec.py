"""
Super Punch-Out!! (SNES) Graphics Codec - CORRECTED v3
Análise corrigida do assembly CODE_0DF9A4

O algoritmo correto é RLE bit-by-bit:
- Lê um control byte
- Para cada um dos 8 bits (ASL a cada iteração):
  * Se carry (bit = 1): lê próximo byte da stream
  * Se não carry (bit = 0): usa valor padrão armazenado
- Escreve 8 bytes de saída por control byte
"""

class GraphicsCodec:
    """Handles compression and decompression of Super Punch-Out!! graphics"""
    
    @staticmethod
    def decompress(data: bytes) -> bytes:
        """
        Decompress Super Punch-Out!! graphics data
        Algoritmo RLE bit-by-bit baseado no assembly CODE_0DF9A4
        
        Args:
            data: Compressed graphics bytes
            
        Returns:
            Decompressed graphics bytes
        """
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("Data must be bytes or bytearray")
        
        if len(data) < 3:
            raise ValueError("Compressed data too small")
        
        output = bytearray()
        pos = 0
        
        # Primeiros 3 bytes são header
        header_byte = data[pos]  # 0x02
        pos += 1
        size_low = data[pos]
        pos += 1
        size_high = data[pos]
        pos += 1
        
        # Valor padrão (default value armazenado em $C8)
        default_value = 0x00
        
        while pos < len(data):
            control_byte = data[pos]
            pos += 1
            
            # Processa cada um dos 8 bits do control byte
            for bit_index in range(8):
                # Verifica o bit (começando do MSB)
                bit = (control_byte >> (7 - bit_index)) & 0x01
                
                if bit == 0:
                    # Bit = 0: usa valor padrão
                    output.append(default_value)
                else:
                    # Bit = 1: lê próximo byte da stream
                    if pos >= len(data):
                        raise ValueError(f"Unexpected end of data at position {pos}")
                    value = data[pos]
                    output.append(value)
                    default_value = value  # Atualiza valor padrão
                    pos += 1
        
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
            return bytes([0x02, 0x00, 0x00])
        
        output = bytearray()
        # Header
        output.append(0x02)
        output.append(len(data) & 0xFF)
        output.append((len(data) >> 8) & 0xFF)
        
        pos = 0
        default_value = 0x00
        
        while pos < len(data):
            control_byte = 0
            literals = bytearray()
            
            # Processa até 8 valores (8 bits)
            for bit_index in range(8):
                if pos < len(data):
                    current = data[pos]
                    
                    if current == default_value:
                        # Bit = 0
                        bit = 0
                    else:
                        # Bit = 1
                        bit = 1
                        default_value = current
                        literals.append(current)
                    
                    control_byte |= (bit << (7 - bit_index))
                    pos += 1
                else:
                    break
            
            output.append(control_byte)
            output.extend(literals)
        
        return bytes(output)
    
    @staticmethod
    def hex_to_bytes(hex_string: str) -> bytes:
        """Convert hex string to bytes"""
        clean_hex = hex_string.replace(' ', '').replace('\n', '').replace('\r', '')
        
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
        
        lines = []
        for i in range(0, len(hex_chars), line_length):
            lines.append(' '.join(hex_chars[i:i + line_length]))
        
        return '\n'.join(lines)
