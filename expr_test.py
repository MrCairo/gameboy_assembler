"""Expression performance test."""

from dmg_asm.core import Expression, Convert

for i in range(0, 65536):
    if i < 10:
        e = Expression(f"00{i}")
    else:
        e = Expression(f"0{i}")
    # print(Convert(e).to_hex16_string())
