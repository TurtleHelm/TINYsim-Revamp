class Trace:
    def __init__(self):
        self.inQueue, self.outQueue, self.prevRegistry, self.prevMemory = [], [], [], []
        self.memory = [0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0]
        self.registry = [0x0,0x0,0x0,0x0]
        self.action = ['', '', '', '']
        self.stop = False
        self.reason = '' 
        
        
    # Setters
    def updateRegistry(self, index:int, val) -> None: self.registry[index] = val
    def updateMemory(self, index:int, val) -> None: self.memory[index] = val
    
    def hasStopped(self, hasStopped:bool=False) -> None: self.stop = hasStopped
    def changeReason(self, reason:str) -> None: self.reason = reason
    
    # Swapping of Registry & Memory Arrays
    def swapPreviousRegistry(self, reg:list) -> None: self.prevRegistry = reg.copy()
    def swapPreviousMemory(self, mem:list) -> None: self.prevMemory = mem.copy()
        
    def incrementIP(self, amt:int) -> None: self.registry[0] += amt

    def setAction(self, newAction:list) -> None:
        for i in range(len(newAction)): self.action[i] = newAction[i]
    
    @staticmethod
    def hexToStr(hexIn:int) -> str:
        """Change from Hexadecimal to Strings

		Args:
		- hexIn (int): Hex Code

		Returns:
		- str: String version of the hex code
		"""
  
        if hexIn > 9: return str(hex(hexIn))[-1].upper()
        else: return str(hexIn)
        
    @staticmethod
    def strToHex(strIn:str) -> int:
        """Change from String to Hexadecimal

		Args:
		- strIn (str): String to be changed

		Returns:
		- int: Hexadecimal Number
		"""
  
        if strIn == "A": return 10
        if strIn == "B": return 11
        if strIn == "C": return 12
        if strIn == "D": return 13
        if strIn == "E": return 14
        if strIn == "F": return 15
        return int(strIn)
    
    @staticmethod
    def printState() -> None:
        """Prints current state of the TINY Machine"""
        printStr = ''
        
        # Registry Values
        for i in range(len(trace.registry)):
            if trace.registry[i] == trace.prevRegistry[i] and count != 0:  printStr += '. '
            else: printStr +=  f'{trace.hexToStr(trace.registry[i])} '
            
        printStr += ' '
        
        trace.swapPreviousRegistry(trace.registry)
        
        # Memory Values
        for i in range(len(trace.memory)):
            if (trace.memory[i] == trace.prevMemory[i] and count != 0): printStr += '.'
            else: printStr += trace.hexToStr(trace.memory[i])
            
        trace.swapPreviousMemory(trace.memory)
        
        printStr += ' '
        
        # Action Values
        for pos in trace.action: printStr += f' {pos}'
        
        print(printStr)

class Operators:
	"""Different Operations used in the TINY Machine
	- HLT: Halt (Stops execution)
	- JMP: Jump (Jumps to designated address)
	- JZE: Jump if Zero (Jumps to designated address if zero flag = 0)
	- JNZ: Jump if not Zero (Jumps to designated address if zero flag != 0)
	- LDA: Load Accumulator (Loads accumulator from designated address)
	- STA: Store Accumulator (Store accumulator to designated address)
	- GET: Get Accumulator (Get accumulator from input queue)
	- PUT: Put Accumulator (Put accumulator into output queue)
	- ROL: Rotate Left (Double and add carry-in)
	- ROR: Rotate Right (Half and carry-out remainder)
	- ADC: Add With Carry
	- CCF: Clear Carry Flag
	- SCF: Set Carry Flag
	- DEL: Decrement Loop Index
	- LDL: Load Loop Index (Load loop index from designated address)
	- FLA: Flip Accumulator
	"""

	def HLT():
		trace.setAction(['HLT', '-', '-', '-'])
		trace.printState()
	
		trace.updateRegistry(2, trace.registry[2] | 0b1000)
		trace.incrementIP(1)
  
		trace.setAction(['', '', '', ''])
		trace.printState()

		trace.hasStopped(True)
		trace.changeReason('Halted Normally')

	def JMP():
		trace.setAction(["JMP", trace.hexToStr(trace.memory[trace.registry[0]+1]), "-", "-"])
		trace.printState()
  
		trace.updateRegistry(0, trace.memory[trace.registry[0]+1])
		
	def JZE():
		trace.setAction(["JZE", trace.hexToStr(trace.memory[trace.registry[0]+1]), "-", "-"])
		trace.printState()
  
		if trace.registry[2] & 0b10 == 0b10: trace.updateRegistry(0, trace.memory[trace.registry[0]+1])
		else: trace.incrementIP(2)

	def JNZ():
		trace.setAction(["JNZ", trace.hexToStr(trace.memory[trace.registry[0]+1]), "-", "-"])
		trace.printState()
  
		if trace.registry[2] & 0b10 != 0b10: trace.updateRegistry(0, trace.memory[trace.registry[0]+1])
		else: trace.incrementIP(2)
		
	def LDA():
		trace.setAction(["LDA", trace.hexToStr(trace.memory[trace.registry[0]+1]), "-", "-"])
		trace.printState()

		trace.updateRegistry(3, trace.memory[trace.memory[trace.registry[0]+1]])
  
		if trace.registry[3] == 0: trace.updateRegistry(2, trace.registry[2] | 0b10)
		else: trace.updateRegistry(2, trace.registry[2] & 0b1101)

		trace.incrementIP(2)

	def STA():
		trace.setAction(["STA", trace.hexToStr(trace.memory[trace.registry[0]+1]), "-", "-"])
		trace.printState()
  
		trace.updateMemory(trace.memory[trace.registry[0]+1], trace.registry[3])
		trace.incrementIP(2)

	def GET():
		if len(trace.inQueue) != 0:
			trace.setAction(["GET", "-", trace.hexToStr(trace.inQueue[0]), "-"])
			trace.printState()
   
			trace.updateRegistry(3, trace.inQueue[0])
			del trace.inQueue[0]
   
			if trace.registry[3] == 0: trace.updateRegistry(2,  trace.registry[2] | 0b10)
			else: trace.updateRegistry(2, trace.registry[2] & 0b1101)

		else:
			trace.setAction(["GET","-","-","-"])
			trace.printState()

			trace.hasStopped(True)
			trace.changeReason('Starved For Input')
   
		trace.incrementIP(1)

	def PUT():
		trace.setAction(["PUT", "-", "-", trace.hexToStr(trace.registry[3])])
		trace.printState()
  
		trace.outQueue.append(trace.registry[3])
		trace.incrementIP(1)

	def ROL():
		trace.setAction(["ROL", "-", "-", "-"])
		trace.printState()
  
		x = trace.registry[3] & 0b1000
		trace.updateRegistry(3, trace.registry[3]*2 + (trace.registry[2] & 0b1))
		if trace.registry[3] >= 16:
			trace.registry[3] -= 16
			trace.updateRegistry(2, trace.registry[2] | 0b1)
   
		else: trace.updateRegistry(2, trace.registry[2] & 0b1110)
  
		if trace.registry[3] & 0b1000 != x: trace.updateRegistry(2, trace.registry[2] | 0b100)
		else: trace.updateRegistry(2, trace.registry[2] & 0b011)
  
		if trace.registry[3] == 0: trace.updateRegistry(2, trace.registry[2] | 0b10)
		else: trace.updateRegistry(2, trace.registry[2] & 0b1101)
  
		trace.incrementIP(1)

	def ROR():
		trace.setAction(["ROR", "-", "-", "-"])
		trace.printState()

		x = trace.registry[3] & 0b1000
  
		if trace.registry[3] % 2 == 0:
			trace.registry[3] /= 2
			trace.registry[2] = trace.registry[2] & 0b1110

		else:
			trace.updateRegistry(3, (trace.registry[3]-1) / 2)
			trace.updateRegistry(2, trace.registry[2] | 0b1)
   
		if trace.registry[3] & 0b1000 != x: trace.updateRegistry(2, trace.registry[2] | 0b100)
		else: trace.updateRegistry(2, trace.registry[2] & 0b011)
  
		if trace.registry[3] == 0: trace.updateRegistry(2, trace.registry[2] | 0b10)
		else: trace.updateRegistry(2, trace.registry[2] & 0b1101)

		trace.incrementIP(1)

	def ADC():
		trace.setAction(["ADC", trace.hexToStr(trace.memory[trace.registry[0]+1]), "-", "-"])
		trace.printState()
  
		carry = 0
  
		if (trace.registry[3] & 0b1) + (trace.memory[trace.memory[trace.registry[0]+1]] & 0b1) + (trace.registry[2] & 0b1) >= 2: carry = 1
		else: carry = 0
		
		if (trace.registry[3] & 0b10)/2 + (trace.memory[trace.memory[trace.registry[0]+1]] & 0b10)/2 + carry >= 2: carry = 1
		else: carry = 0
		
		if (trace.registry[3] & 0b100)/4 + (trace.memory[trace.memory[trace.registry[0]+1]] & 0b100)/4 + carry >= 2: carry = 1
		else: carry = 0
		
		if (trace.registry[3] & 0b1000)/8 + (trace.memory[trace.memory[trace.registry[0]+1]] & 0b1000)/8 + carry >= 2: carry2 = 1
		else: carry2 = 0

		if carry2 == carry: trace.updateRegistry(2, trace.registry[2] & 0b1011)
		else: trace.updateRegistry(2, trace.registry[2] | 0b0100)
		
		trace.updateRegistry(3, trace.registry[3] + (trace.registry[2] & 0b1) + trace.memory[trace.memory[trace.registry[0]+1]])
		
		if trace.registry[3] >=16:
			trace.registry[3] -= 16
			trace.updateRegistry(2, trace.registry[2] | 0b1)
	
		else: trace.updateRegistry(2, trace.registry[2] & 0b1110)
		
		if trace.registry[3] == 0: trace.updateRegistry(2, trace.registry[2] | 0b10)
		else: trace.updateRegistry(2, trace.registry[2] & 0b1101)
		
		trace.incrementIP(2)

	def CCF():
		trace.setAction(["CCF", "-", "-", "-"])
		trace.printState()
	
		trace.updateRegistry(2, trace.registry[2] & 0b1110)
		trace.incrementIP(1)

	def SCF():
		trace.setAction(["SCF", "-", "-", "-"])
		trace.printState()
  
		trace.updateRegistry(2, trace.registry[2] | 0b0001)
		trace.incrementIP(1)

	def DEL():
		trace.setAction(["DEL", "-", "-", "-"])
		trace.printState()
  
		trace.registry[1] -= 1
		if trace.registry[1] < 0: trace.registry[1] += 16

		if trace.registry[1] == 0: trace.updateRegistry(2, trace.registry[2] | 0b0010)
		else: trace.updateRegistry(2, trace.registry[2] & 0b1101)
  
		trace.incrementIP(1)

	def LDL():
		trace.setAction(["LDL", trace.hexToStr(trace.memory[trace.registry[0]+1]), "-", "-"])
		trace.printState()
  
		trace.updateRegistry(1, trace.memory[trace.memory[trace.registry[0]+1]])
  
		if trace.registry[1] == 0: trace.updateRegistry(2, trace.registry[2] | 0b0010)
		else: trace.updateRegistry(2, trace.registry[2] & 0b1101)
  
		trace.incrementIP(2)

	def FLA():
		trace.setAction(["FLA", "-", "-", "-"])
		trace.printState()
  
		trace.updateRegistry(3, 15 - trace.registry[3])
		if trace.registry[3] < 0: trace.registry[3] += 16

		if trace.registry[3] == 0: trace.updateRegistry(2, trace.registry[2] | 0b0010)
		else: trace.updateRegistry(2, trace.registry[2] & 0b1101)
  
		trace.incrementIP(1)

trace = Trace()

def main():
	global count

	inputString = input('Enter input queue (Format: x, x, x, x...): ').replace(', ','')
	for char in inputString: trace.inQueue.append(trace.strToHex(char))

	inputString = input('Enter TINY configuration (Format: x x x x  xxxxxxxxxxxxxxx): ').replace(' ', '')

	# Trace Header
	print('I L F A  Memory----------  Action---')
	print('P I R C  0123456789ABCDEF  OPR & ? !')
	print('-------  ----------------  ---------')

	x = 0

	for char in inputString:
		if x < 20:
			if x < 4: trace.registry[x] = trace.strToHex(char)
			else: trace.memory[x-4] = trace.strToHex(char)
		x += 1

	# Default Registry & Memory Values to Check Against
	trace.swapPreviousRegistry(trace.registry)
	trace.swapPreviousMemory(trace.memory)

	count = 0 # Iterations Through Trace

	while not trace.stop:
		if count >= 500:
			trace.stop = True
			trace.reason = "Loops Henceforth"

		match trace.memory[trace.registry[0]]:
			case 0: Operators.HLT()
			case 1: Operators.JMP()
			case 2: Operators.JZE()
			case 3: Operators.JNZ()
			case 4: Operators.LDA()
			case 5: Operators.STA()
			case 6: Operators.GET()
			case 7: Operators.PUT()
			case 8: Operators.ROL()
			case 9: Operators.ROR()
			case 10: Operators.ADC()
			case 11: Operators.CCF()
			case 12: Operators.SCF()
			case 13: Operators.DEL()
			case 14: Operators.LDL()
			case 15: Operators.FLA()
			case _: print('Error: Exceeded TINY Operator List')

		count += 1

	print('-------  ----------------  ---------')
	print(trace.reason)
	input('Enter to Exit...')
 
main()