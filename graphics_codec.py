"""
Super Punch-Out!! (SNES) Graphics Codec - CORRECTED v2
Análise corrigida do assembly CODE_0DF9A4

Formato real:
- Cada control byte controla 4 valores (nibbles/pares de bits)
- Cada par de bits (2 bits) indica:
  00 = usar valor padrão ($C8)
  01 = ler próximo byte da stream
  10 = (pode ser repeat ou outra operação)
  11 = ler próximo byte da stream

O valor padrão ($C8) é armazenado em um registro e pode ser alterado.
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
        
        if len(data) < 3:
            raise ValueError("Compressed data too small")
        
        output = bytearray()
        pos = 0
        
        # Header: primeiros 3 bytes
        header_byte = data[pos]  # 0x02
        pos += 1
        size_low = data[pos]
        pos += 1
        size_high = data[pos]
        pos += 1
        
        # Valor padrão inicial
        default_value = 0x00
        
        while pos < len(data):
            control_byte = data[pos]
            pos += 1
            
            # Processa 4 pares de bits (do MSB para LSB)
            for i in range(4):
                # Extrai par de bits
                pair = (control_byte >> (6 - i * 2)) & 0x03
                
                if pair == 0:
                    # Usa valor padrão
                    output.append(default_value)
                elif pair == 1 or pair == 3:
                    # Lê valor da stream
                    if pos >= len(data):
                        raise ValueError(f"Unexpected end of data at position {pos}")
                    value = data[pos]
                    output.append(value)
                    
                    # Se pair == 1, esse valor se torna o novo padrão
                    if pair == 1:
                        default_value = value
                    
                    pos += 1
                else:  # pair == 2
                    # Lê valor da stream (pode ser especial)
                    if pos >= len(data):
                        raise ValueError(f"Unexpected end of data at position {pos}")
                    value = data[pos]
                    output.append(value)
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
            
            # Processa até 4 valores
            for i in range(4):
                if pos < len(data):
                    current = data[pos]
                    
                    if current == default_value:
                        # Usa par 00
                        pair = 0
                    else:
                        # Usa par 01 (lê e atualiza padrão)
                        pair = 1
                        default_value = current
                        literals.append(current)
                    
                    control_byte |= (pair << (6 - i * 2))
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
