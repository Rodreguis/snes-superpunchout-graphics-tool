"""
Super Punch-Out!! (SNES) Graphics Codec - CORRECTED
Análise do assembly CODE_0DF9A4 revela o formato real

O formato usa uma sequência de pares de bits como controle:
- Cada byte tem 8 bits = 4 pares de controle
- Cada par de bits (2 bits) controla se o próximo valor é:
  00 = usar valor padrão ($C8)
  01 = ler valor da stream
  10 = ler valor da stream (parece duplicado, mas pode ter propósito)
  11 = ler valor da stream

Depois escreve 4 bytes por ciclo de 8 bytes de entrada (aprox.)
"""

class GraphicsCodec:
    """Handles compression and decompression of Super Punch-Out!! graphics"""
    
    @staticmethod
    def decompress(data: bytes) -> bytes:
        """
        Decompress Super Punch-Out!! graphics data
        Algoritmo baseado na análise do assembly CODE_0DF9A4
        
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
        
        # Primeiros 3 bytes parecem ser header
        # Byte 0: sempre 02?
        # Byte 1-2: tamanho ou outro dado
        header_byte = data[pos]
        pos += 1
        
        # Tamanho codificado ou ignorar
        size_low = data[pos]
        pos += 1
        size_high = data[pos]
        pos += 1
        
        # Byte padrão (default value para nibble 00)
        default_value = 0x00
        
        while pos < len(data):
            control_byte = data[pos]
            pos += 1
            
            # Processa cada par de bits
            for i in range(4):
                # Extrai par de bits (do MSB para LSB)
                pair = (control_byte >> (6 - i * 2)) & 0x03
                
                if pair == 0:
                    # Usa valor padrão
                    output.append(default_value)
                elif pair == 1:
                    # Lê valor da stream
                    if pos >= len(data):
                        raise ValueError(f"Unexpected end of data at position {pos}")
                    value = data[pos]
                    output.append(value)
                    pos += 1
                elif pair == 2:
                    # Lê valor da stream (aparentemente mesmo que 01)
                    if pos >= len(data):
                        raise ValueError(f"Unexpected end of data at position {pos}")
                    value = data[pos]
                    output.append(value)
                    pos += 1
                else:  # pair == 3
                    # Lê valor da stream
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
        while pos < len(data):
            control_byte = 0
            literals = bytearray()
            
            # Processa até 4 valores (4 pares de bits)
            for i in range(4):
                if pos < len(data):
                    # Decide se usa valor padrão (00) ou literal (01/11)
                    # Simplificado: sempre usa literal para garantir reconstrução correta
                    pair = 1  # ou 3, ambos leem da stream
                    control_byte |= (pair << (6 - i * 2))
                    literals.append(data[pos])
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
