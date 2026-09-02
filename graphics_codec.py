"""
Super Punch-Out!! (SNES) Graphics Codec - CORRECTED v4
Análise corrigida do assembly CODE_0DF9A4

O algoritmo correto processa dados em blocos:
- Cada bloco começa com um byte de controle
- O byte de controle possui um bit especial (bit 7) que indica:
  * Se bit 7 = 0: próximo byte é o tamanho do bloco literal
  * Se bit 7 = 1: próximo byte é o valor a repetir e o tamanho
  
Ou alternativamente:
- Byte de controle = 0x00 indica fim de dados
- Quando encontra 0x00, para de descompactar
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
        
        # Primeiros 3 bytes são header
        header_byte = data[pos]  # 0x02
        pos += 1
        size_low = data[pos]
        pos += 1
        size_high = data[pos]
        pos += 1
        
        # Valor padrão (default value)
        default_value = 0x00
        
        while pos < len(data):
            control_byte = data[pos]
            pos += 1
            
            # Se encontrar 0x00, pode indicar fim
            if control_byte == 0x00:
                break
            
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
                        # Se chegou ao fim, completa com valor padrão se necessário
                        return bytes(output)
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
        
        # Adiciona terminador
        output.append(0x00)
        
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
