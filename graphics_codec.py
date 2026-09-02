"""
Super Punch-Out!! (SNES) Graphics Codec - CORRECTED v6
Análise FINAL corrigida

Formato real - Nibble RLE (2 bits por valor):
- Byte 0 ($C4): Número de control bytes
- Byte 1: Reservado
- Byte 2 ($C7): Número de blocos (iterações do loop externo)
- Cada control byte codifica 4 valores (4 nibbles de 2 bits cada)
- Cada par de bits (nibble):
  * 00 = usar valor padrão ($C8)
  * 01 = ler próximo byte, usar como valor padrão
  * 10 = usar valor padrão (pode ser variant)
  * 11 = ler próximo byte da stream
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
        
        # Header
        num_control_bytes = data[pos]
        pos += 1
        unknown = data[pos]
        pos += 1
        num_blocks = data[pos]
        pos += 1
        
        # Valor padrão
        default_value = 0x00
        
        # Loop externo: repete num_blocks vezes
        for block_idx in range(num_blocks):
            if pos >= len(data):
                break
            
            control_byte = data[pos]
            pos += 1
            
            # Processa 4 pares de bits (nibbles)
            for nibble_idx in range(4):
                # Extrai par de bits (2 bits por nibble)
                nibble = (control_byte >> (6 - nibble_idx * 2)) & 0x03
                
                if nibble == 0:
                    # 00: usa valor padrão
                    output.append(default_value)
                elif nibble == 1:
                    # 01: lê valor e atualiza padrão
                    if pos >= len(data):
                        return bytes(output)
                    value = data[pos]
                    output.append(value)
                    default_value = value
                    pos += 1
                elif nibble == 2:
                    # 10: usa valor padrão (ou read without update)
                    if pos >= len(data):
                        output.append(default_value)
                    else:
                        value = data[pos]
                        output.append(value)
                        pos += 1
                else:  # nibble == 3
                    # 11: lê valor da stream (sem atualizar padrão)
                    if pos >= len(data):
                        return bytes(output)
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
            return bytes([0x00, 0x00, 0x00])
        
        output = bytearray()
        pos = 0
        default_value = 0x00
        control_bytes = bytearray()
        all_literals = bytearray()
        
        # Processa dados em blocos de 4 valores
        while pos < len(data):
            control_byte = 0
            literals = bytearray()
            
            # Processa até 4 valores (4 nibbles)
            for nibble_idx in range(4):
                if pos < len(data):
                    current = data[pos]
                    
                    if current == default_value:
                        # 00: valor padrão
                        nibble = 0
                    else:
                        # 01: ler e atualizar padrão
                        nibble = 1
                        default_value = current
                        literals.append(current)
                    
                    control_byte |= (nibble << (6 - nibble_idx * 2))
                    pos += 1
                else:
                    break
            
            control_bytes.append(control_byte)
            all_literals.extend(literals)
        
        # Header
        num_control_bytes = len(control_bytes)
        output.append(num_control_bytes & 0xFF)
        output.append(0x00)
        output.append(num_control_bytes & 0xFF)
        
        # Dados
        output.extend(control_bytes)
        output.extend(all_literals)
        
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
