"""
Super Punch-Out!! (SNES) Graphics Codec - CORRECTED v5
Análise FINAL do assembly CODE_0DF9A4

Estrutura correta:
- Byte 0 ($C4): Tamanho da stream de entrada (número de control bytes)
- Byte 1: Ignorado ou reservado
- Byte 2 ($C7): Número de iterações/blocos do loop externo
- Bytes 3+: Dados comprimidos

Loop externo: repete $C7 vezes
  Loop interno: processa 8 valores por control byte
    Para cada bit do control byte (ASL):
      - Se carry = 0: usar valor padrão ($C8)
      - Se carry = 1: ler próximo byte, usar e atualizar $C8
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
        stream_size = data[pos]  # $C4 - número de control bytes
        pos += 1
        unknown = data[pos]  # byte não usado ou reservado
        pos += 1
        num_blocks = data[pos]  # $C7 - número de blocos/iterações
        pos += 1
        
        # Valor padrão
        default_value = 0x00
        
        # Loop externo: repete num_blocks vezes
        for block_idx in range(num_blocks):
            # Lê um novo control byte
            if pos >= len(data):
                break
            
            control_byte = data[pos]
            pos += 1
            
            # Loop interno: processa 8 bits/valores
            for bit_idx in range(8):
                # Verifica carry do ASL
                bit = (control_byte >> (7 - bit_idx)) & 0x01
                
                if bit == 0:
                    # Carry = 0: usa valor padrão
                    output.append(default_value)
                else:
                    # Carry = 1: lê próximo byte
                    if pos >= len(data):
                        return bytes(output)
                    value = data[pos]
                    output.append(value)
                    default_value = value  # Atualiza padrão
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
        
        # Processa dados em blocos de 8 valores
        while pos < len(data):
            control_byte = 0
            literals = bytearray()
            
            # Processa até 8 valores
            for bit_idx in range(8):
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
                    
                    control_byte |= (bit << (7 - bit_idx))
                    pos += 1
                else:
                    break
            
            control_bytes.append(control_byte)
            all_literals.extend(literals)
        
        # Header
        num_control_bytes = len(control_bytes)
        output.append(num_control_bytes & 0xFF)  # $C4
        output.append(0x00)  # byte não usado
        output.append(num_control_bytes & 0xFF)  # $C7 (mesmo que $C4)
        
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
