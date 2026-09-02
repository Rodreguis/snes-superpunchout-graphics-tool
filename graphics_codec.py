"""
Super Punch-Out!! (SNES) Graphics Codec - CORRECTED v7 FINAL
Análise CORRETA do assembly CODE_0DF9A4 e CODE_0DF8FD

Estrutura correta:
- Byte 0 ($C4): Tamanho da stream (número total de control bytes a processar)
- Byte 1: Ignorado/reservado
- Byte 2 ($C7): Número de iterações do loop interno
- Bytes 3+: Dados comprimidos

Algoritmo:
1. Loop externo: Lê um novo control byte e carrega em $C8 (valor padrão) ANTES de processar
2. Loop interno (8 iterações): Processa 8 bits do control byte com ASL
   - BCS = bit é 1: ler próximo byte, usar e atualizar $C8
   - BCC = bit é 0: usar valor em $C8 (padrão)

A chave está em: LDA.w DATA_...,y / INY / STA.b $C8
Isso carrega o PRIMEIRO byte de cada bloco como valor padrão!
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
        unknown = data[pos]  # byte não usado
        pos += 1
        num_iterations = data[pos]  # $C7 - número de iterações do loop interno
        pos += 1
        
        # Valor padrão
        default_value = 0x00
        
        # Loop externo: processa cada control byte
        for block_idx in range(stream_size):
            if pos >= len(data):
                break
            
            # Carrega novo byte como valor padrão e como control byte
            default_value = data[pos]
            control_byte = data[pos]
            pos += 1
            
            # Loop interno: processa 8 bits do control byte
            for bit_idx in range(8):
                # ASL: rotaciona controle byte à esquerda, bit vai para carry
                bit = (control_byte >> (7 - bit_idx)) & 0x01
                
                if bit == 0:
                    # BCC (no carry): usa valor padrão
                    output.append(default_value)
                else:
                    # BCS (carry): lê próximo byte
                    if pos >= len(data):
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
            return bytes([0x00, 0x00, 0x00])
        
        output = bytearray()
        pos = 0
        default_value = 0x00
        control_bytes = bytearray()
        all_literals = bytearray()
        
        # Processa dados em blocos de 8 valores
        while pos < len(data):
            current = data[pos]
            
            # Primeiro byte do bloco é sempre o novo valor padrão
            default_value = current
            control_byte = 0x00
            literals = bytearray()
            
            output_count = 0
            
            # Processa até 8 valores
            for bit_idx in range(8):
                if pos < len(data):
                    if output_count == 0:
                        # Primeiro valor: sempre vai como valor padrão
                        bit = 0
                        output_count += 1
                        pos += 1
                    else:
                        current = data[pos]
                        
                        if current == default_value:
                            # Bit = 0: valor padrão
                            bit = 0
                        else:
                            # Bit = 1: ler e atualizar padrão
                            bit = 1
                            default_value = current
                            literals.append(current)
                        
                        output_count += 1
                        pos += 1
                else:
                    break
                
                control_byte |= (bit << (7 - bit_idx))
            
            control_bytes.append(control_byte)
            all_literals.extend(literals)
        
        # Header
        num_control_bytes = len(control_bytes)
        output.append(num_control_bytes & 0xFF)  # $C4
        output.append(0x00)  # byte não usado
        output.append(num_control_bytes & 0xFF)  # $C7
        
        # Dados: control bytes + literals intercalados
        # Na verdade, o primeiro byte de cada bloco é carregado como control byte E como valor padrão
        # Portanto, estrutura é: [control_byte_1] [literals_1] [control_byte_2] [literals_2] ...
        for i, control_byte in enumerate(control_bytes):
            output.append(control_byte)
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
