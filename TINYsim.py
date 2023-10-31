class Trace:
	def __init__(self):
		# TINY Memory (16 Bit)
		self.prevMem = [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
		self.memory = [0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0]

		# TINY Registry (4 Bit)
		self.registry = [0x0,0x0,0x0,0x0]
		self.prevReg = [0x0, 0x0, 0x0, 0x0]
		self.inQueue, self.outQueue = [], []
		self.action = ['', '', '', '']
		self.stop = False
		self.reason = ''

	def incrementIP(self, amt:int) -> None:
		self.registry[0] += amt
		if self.registry[0] >= 16: self.registry[0] -= 16

	def setAction(self, newAction:list) -> None:
		"""Set New Action List

		Args:
			newAction (list): new action list to append
		"""
		for i in range(len(newAction)): self.action[i] = newAction[i]

	@staticmethod
	def hexToStr(hexIn:int) -> str:
		"""Convert from Hexadecimal to Strings

		Args:
			hexIn (int): Hex Code to Take In

		Returns:
			str: Stringified Hexadecimal
		"""
		if hexIn > 9: return str(hex(hexIn))[-1].upper()
		else: return str(hexIn)

	@staticmethod
	def strToHex(strIn) -> int:
		"""Convert From Stringified Hexadecimal to Hex Codes

		Args:
			strIn (str): String to Convert

		Returns:
			int: Hex Code
		"""
	
		if strIn == "A": return 10
		if strIn == "B": return 11
		if strIn == "C": return 12
		if strIn == "D": return 13
		if strIn == "E": return 14
		if strIn == "F": return 15
		return int(strIn)

	def printState(self) -> None:
		"""Prints current state of the TINY Machine"""

		printStr = ''

		for i in range(len(self.registry)):
			if self.registry[i] == self.prevReg[i] and count != 0: printStr += '. '
			else: printStr += f'{self.hexToStr(self.registry[i])} '  

		printStr += ' '
		self.prevReg = self.registry.copy()

		for i in range(len(self.memory)):
			if self.memory[i] == self.prevMem[i] and count != 0: printStr += '.'
			else: printStr += self.hexToStr(self.memory[i])

		printStr += ' '
		self.prevMem = self.memory.copy()
	
		for pos in self.action: printStr += f' {pos}'
		
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
    
    def __init__(self, trace:Trace): self.trace = trace
    
    def HLT(self) -> None:
        self.trace.setAction(['HLT', '-', '-', '-'])
        self.trace.printState()
        
        self.trace.registry[2] = self.trace.registry[2] | 0b1000
        self.trace.incrementIP(1)
        
        self.trace.setAction(["","","",""])
        self.trace.printState()
        
        self.trace.stop = True
        self.trace.reason = "Halted Normally"
        
    def JMP(self) -> None:
        self.trace.setAction(['JMP', self.trace.hexToStr(self.trace.memory[self.trace.registry[0]+1]), '-', '-'])
        self.trace.printState()
        
        self.trace.registry[0] = self.trace.memory[self.trace.registry[0]+1]
            
    def JZE(self) -> None:
        self.trace.setAction(["JZE", self.trace.hexToStr(self.trace.memory[self.trace.registry[0]+1]),"-","-"])
        self.trace.printState()
        
        if self.trace.registry[2] & 0b10 == 0b10: self.trace.registry[0] = self.trace.memory[self.trace.registry[0]+1]
        else: self.trace.incrementIP(2)
        
    def JNZ(self) -> None:
        self.trace.setAction(["JNZ", self.trace.hexToStr(self.trace.memory[self.trace.registry[0]+1]),"-","-"])
        self.trace.printState()
        
        if self.trace.registry[2] & 0b10 != 0b10: self.trace.registry[0] = self.trace.memory[self.trace.registry[0]+1]
        else: self.trace.incrementIP(2)
        
    def LDA(self) -> None:
        self.trace.setAction(["LDA", self.trace.hexToStr(self.trace.memory[self.trace.registry[0]+1]),"-","-"])
        self.trace.printState()
        
        self.trace.registry[3] = self.trace.memory[self.trace.memory[self.trace.registry[0]+1]]
        
        if self.trace.registry[3] == 0: self.trace.registry[2] = self.trace.registry[2] | 0b10
        else: self.trace.registry[2] = self.trace.registry[2] & 0b1101
        
        self.trace.incrementIP(2)
        
    def STA(self) -> None:
        self.trace.setAction(["STA", self.trace.hexToStr(self.trace.memory[self.trace.registry[0]+1]),"-","-"])
        self.trace.printState()
        
        self.trace.memory[self.trace.memory[self.trace.registry[0]+1]] = self.trace.registry[3]
        self.trace.incrementIP(2)
        
    def GET(self) -> None:
        if len(self.trace.inQueue) != 0:
            self.trace.setAction(["GET","-", self.trace.hexToStr(self.trace.inQueue[0]),"-"])
            self.trace.printState()
            
            self.trace.registry[3] = self.trace.inQueue[0]
            
            del self.trace.inQueue[0]
            
            if self.trace.registry[3] == 0: self.trace.registry[2] = self.trace.registry[2] | 0b10
            else: self.trace.registry[2] = self.trace.registry[2] & 0b1101
            
        else:
            self.trace.setAction(["GET","-","-","-"])
            self.trace.printState()
            
            self.trace.stop = True
            self.trace.reason = "Starved For Input"
            
        self.trace.incrementIP(1)
        
    def PUT(self) -> None:
        self.trace.setAction(["PUT","-","-",self.trace.hexToStr(self.trace.registry[3])])
        self.trace.printState()
        
        self.trace.outQueue.append(self.trace.registry[3])
        self.trace.incrementIP(1)
        
    def ROL(self) -> None:
        self.trace.setAction(["ROL","-","-","-"])
        self.trace.printState()
        
        self.trace.registry[3] = self.trace.registry[3] * 2 + (self.trace.registry[2] & 0b1)
        
        if self.trace.registry[3] >= 16:
            self.trace.registry[3] -= 16
            self.trace.registry[2] = self.trace.registry[2] | 0b1
            
        else: self.trace.registry[2] = self.trace.registry[2] & 0b1110
        
        if self.trace.registry[3] & 0b1000 != (self.trace.registry[3] & 0b1000):
            self.trace.registry[2] = self.trace.registry[2] | 0b100
        else: self.trace.registry[2] = self.trace.registry[2] & 0b011
        
        if self.trace.registry[3] == 0: self.trace.registry[2] = self.trace.registry[2] | 0b10
        else: self.trace.registry[2] = self.trace.registry[2] & 0b1101
        
        self.trace.incrementIP(1)
        
    def ROR(self) -> None:
        self.trace.setAction(["ROR","-","-","-"])
        self.trace.printState()
        
        x = self.trace.registry[3] & 0b1000
        if self.trace.registry[3] % 2 == 0:
            self.trace.registry[3]/=2
            self.trace.registry[2] = self.trace.registry[2] & 0b1110
        else:
            self.trace.registry[3] = (self.trace.registry[3]-1) / 2
            self.trace.registry[2] = self.trace.registry[2] | 0b1
            
        if self.trace.registry[3] & 0b1000 != x: self.trace.registry[2] = self.trace.registry[2] | 0b100
        else: self.trace.registry[2] = self.trace.registry[2] & 0b011
            
        if self.trace.registry[3] == 0: self.trace.registry[2] = self.trace.registry[2] | 0b10
        else: self.trace.registry[2] = self.trace.registry[2] & 0b1101
        
        self.trace.incrementIP(1)
        
    def ADC(self) -> None:
        self.trace.setAction(["ADC", self.trace.hexToStr(self.trace.memory[self.trace.registry[0]+1]),"-","-"])
        self.trace.printState()
        carry = 0
        
        if(self.trace.registry[3] & 0b1) + (self.trace.memory[self.trace.memory[self.trace.registry[0]+1]] & 0b1) + (self.trace.registry[2] & 0b1) >= 2: carry = 1
        else: carry = 0
        
        if(self.trace.registry[3] & 0b10)/2 + (self.trace.memory[self.trace.memory[self.trace.registry[0]+1]] & 0b10)/2 + carry >= 2: carry = 1
        else: carry = 0
        
        if(self.trace.registry[3] & 0b100)/4 + (self.trace.memory[self.trace.memory[self.trace.registry[0]+1]] & 0b100)/4 + carry >= 2: carry = 1
        else: carry = 0
        
        if(self.trace.registry[3] & 0b1000)/8 + (self.trace.memory[self.trace.memory[self.trace.registry[0]+1]] & 0b1000)/8 + carry >= 2: carry2 = 1
        else: carry2 = 0
        
        if carry2 == carry: self.trace.registry[2] = self.trace.registry[2] & 0b1011
        else: self.trace.registry[2] = self.trace.registry[2] | 0b0100
        
        self.trace.registry[3] = self.trace.registry[3] + (self.trace.registry[2] & 0b1) + self.trace.memory[self.trace.memory[self.trace.registry[0]+1]]
        
        if self.trace.registry[3] >=16:
            self.trace.registry[3] -= 16
            self.trace.registry[2] = self.trace.registry[2] | 0b1
        
        else: self.trace.registry[2] = self.trace.registry[2] & 0b1110
        
        if self.trace.registry[3] == 0: self.trace.registry[2] = self.trace.registry[2] | 0b10
        else: self.trace.registry[2] = self.trace.registry[2] & 0b1101
        
        self.trace.incrementIP(2)
        
    def CCF(self) -> None:
        self.trace.setAction(["CCF","-","-","-"])
        self.trace.printState()
        
        self.trace.registry[2] = self.trace.registry[2] & 0b1110
        self.trace.incrementIP(1)
        
    def SCF(self) -> None:
        self.trace.setAction(["SCF","-","-","-"])
        self.trace.printState()
        
        self.trace.registry[2] = self.trace.registry[2] | 0b0001
        self.trace.incrementIP(1)
        
    def DEL(self) -> None:
        self.trace.setAction(["DEL","-","-","-"])
        self.trace.printState()
        
        self.trace.registry[1]-=1
        
        if self.trace.registry[1]<0: self.trace.registry[1]+=16
        
        if self.trace.registry[1] == 0: self.trace.registry[2] = self.trace.registry[2] | 0b0010
        else: self.trace.registry[2] = self.trace.registry[2] & 0b1101
        
        self.trace.incrementIP(1)
        
    def LDL(self) -> None:
        self.trace.setAction(["LDL", self.trace.hexToStr(self.trace.memory[self.trace.registry[0]+1]),"-","-"])
        self.trace.printState()
        
        self.trace.registry[1] = self.trace.memory[self.trace.memory[self.trace.registry[0]+1]]
        if self.trace.registry[1] == 0: self.trace.registry[2] = self.trace.registry[2] | 0b0010
        else: self.trace.registry[2] = self.trace.registry[2] & 0b1101
        
        self.trace.incrementIP(2)
        
    def FLA(self) -> None:
        self.trace.setAction(["FLA","-","-","-"])
        self.trace.printState()
        
        self.trace.registry[3] = 15 - self.trace.registry[3]
        
        if self.trace.registry[3] < 0: self.trace.registry[3]+=1
        if self.trace.registry[3] == 0: self.trace.registry[2] = self.trace.registry[2] | 0b0010
        else: self.trace.registry[2] = self.trace.registry[2] & 0b1101
        
        self.trace.incrementIP(1)

trace = Trace()

def main(tinyTrace:Trace) -> None:
	"""Main Function

	Args:
		trace (Trace): Current Trace Instance
	"""
    
	ops = Operators(tinyTrace)
    
	inputString = input('Enter input queue (Format: x, x, x, x...): ').replace(', ','')
	for char in inputString: tinyTrace.inQueue.append(tinyTrace.strToHex(char))

	inputString = input('Enter TINY configuration (Format: x x x x  xxxxxxxxxxxxxxx): ').replace(' ', '')

	# Load data into arrays
	for i, char in enumerate(inputString):
		if i < 20:
			if i < 4: tinyTrace.registry[i] = tinyTrace.strToHex(char)
			else: tinyTrace.memory[i-4] = tinyTrace.strToHex(char)

		i += 1

	tinyTrace.prevReg = tinyTrace.registry.copy()
	tinyTrace.prevMem = tinyTrace.memory.copy()

	# Trace Header
	print('I L F A  Memory----------  Action---')
	print('P I R C  0123456789ABCDEF  OPR & ? !')
	print('-------  ----------------  ---------')
 
	global count
	count = 0 # Iterations Through Trace

	# Apply Operators to Traces
	while not tinyTrace.stop:
		if count >= 500:
			trace.stop = True
			trace.reason = "Loops Henceforth"

		match tinyTrace.memory[tinyTrace.registry[0]]:
			case 0: ops.HLT()
			case 1: ops.JMP()
			case 2: ops.JZE()
			case 3: ops.JNZ()
			case 4: ops.LDA()
			case 5: ops.STA()
			case 6: ops.GET()
			case 7: ops.PUT()
			case 8: ops.ROL()
			case 9: ops.ROR()
			case 10: ops.ADC()
			case 11: ops.CCF()
			case 12: ops.SCF()
			case 13: ops.DEL()
			case 14: ops.LDL()
			case 15: ops.FLA()
			case _: print('Error: Exceeded TINY Operator List')

		count += 1

	print('-------  ----------------  ---------')
	print(f'        {tinyTrace.reason}         ')
	print('-------  ----------------  ---------')
	input('Hit Enter to Finish...')

main(trace)