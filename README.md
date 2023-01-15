# tasmota_script_minimizer
A tool to minimize Tasmota scripts.
```bash
  Name            : tasmota_script_minimizer.py
  Created By      : Thomas Messmer
  Blog            : http://thomas-messmer.com
  Documentation   : https://github.com/Zumili/tasmota_script_minimizer
  License         : The MIT License
  Version         : 0.1.0
```

## How to install?

`git clone https://github.com/Zumili/tasmota_script_minimizer`

## How to run?

`python tasmota_script_minimizer.py -h`

```bash
 Options Short/Long  | Type | Description
 ====================+======+=========================================  
 -a, --aggressivity  | Num  | aggressivity of minimization [0-5]
 -d, --dictprint     | Num  | print dictionary [0-2]
 -i, --info          |      | print tool information
 -o, --output        | Str  | output file name
```

### Examples

Minimize Tasmota script with default parameters, testscript%Y_%m_%d-%H_%M_%S.txt will be created.  
`python tasmota_script_minimizer.py testscript.txt`

Minimize Tasmota script with aggressivity=3, print a dictionary and minimized.txt will be created.  
`python python tasmota_script_minimizer.py testscript.txt -o minimized.txt -a 3 -d 1`

## Version
0.1.0

## License
[The MIT License](https://opensource.org/licenses/MIT)

## Who?
Written by Thomas Messmer ([thomas-messmer.com](http://thomas-messmer.com)) for scientific purposes only.
