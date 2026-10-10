"""Check authored quotations before submitting immutable observations."""
import ast
import sys
from pathlib import Path
from secfragility.reader import block_for
root=Path(__file__).resolve().parents[1]
for number in sys.argv[1:]:
    path=root/'work'/f'extension_authored_{number}.py'
    tree=ast.parse(path.read_text())
    key=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and isinstance(x.targets[0],ast.Name) and x.targets[0].id=='k')
    text=block_for(root,key)['text']
    for call in ast.walk(tree):
        if not isinstance(call,ast.Call):continue
        quotes=([call.args[2]] if isinstance(call.func,ast.Name) and call.func.id=='tagged' else [])+[x.value for x in call.keywords if x.arg=='quote']
        for quote in quotes:
            value=ast.literal_eval(quote)
            assert value in text,(number,value)
    print(number,'quotes_valid')
