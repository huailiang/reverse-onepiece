#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Author: penghuailiang
# @Date  : 2019-08-14


import os
import sys
import re


def IsDefVtx(i, bits): 
	"""
	查找结束$VTX
    """
	if i > len(bits)-4:  
		return False
	if bits[i] == 36 and bits[i+1] == 86 and bits[i+2] == 84 and bits[i+3] == 88:
		return True
	return False
		

def IsDefCt0(i, bits): 
	"""
    查找结束$CT0
    """
	if i>len(bits) - 4:
		return False
	if bits[i] == 36 and bits[i+1] == 67 and bits[i+2] == 84 and bits[i+3] == 48:
		return True
	return False


def IsDefRsi(i, bits):
	"""
    查找结束$RSI
    """
	if i>len(bits) - 4:
		return False
	if bits[i] == 36 and bits[i+1] == 82 and bits[i+2] == 83 and bits[i+3] == 73:
		return True
	return False


def IsDef3000(i, bits):
    if i>len(bits) - 4:
    	return False
    if bits[i] == 48 and bits[i+1] == 0 and bits[i+2] == 0 and bits[i+3] == 0:
    	return True;
	return False

def PrintFVF(start, end, bits):
	"""
	输出 FVF Offset & size UVB
	"""
	offset = 0
	addr = 0
	indx = start + 24
	vtx = pow(16, 6) * bits[indx + 3] + pow(16, 4) * bits[indx + 2] + pow(16, 2) * bits[indx + 1] + bits[indx]
	for i in range(end - start):
		if IsDef3000(i + start, bits) and offset == 0:
			indx = i + start + 12  #面的数量相距3000为12bit
			offset = pow(16, 6) * bits[indx + 3] + pow(16, 4) * bits[indx + 2] + pow(16, 2) * bits[indx + 1] + bits[indx]
		if IsDefRsi(i + start, bits) and addr == 0 and offset > 0:
			indx =  i + start + 32
			addr = pow(16, 4) * bits[indx + 2] + pow(16, 2) * bits[indx + 1] + bits[indx]
			print("FVF   addr: %x"%(offset + addr))
			indx = indx + 4
			temp = pow(16, 6) * bits[indx + 3] + pow(16, 4) * bits[indx + 2] + pow(16, 2) * bits[indx + 1] + bits[indx]
			uvb = (temp - offset) / vtx
			print("size   UVB: %d"%(uvb))



def Prin4f(i, tag, bits, div=1):
	"""
	反着十进制输出
	"""
	# print("hex %s: %x%x%x%x"%(tag, bits[i+3], bits[i+2], bits[i+1], bits[i])) #十六进制
	dec = bits[i+3] * pow(16, 6) + bits[i+2] * pow(16, 4) + bits[i+1] * pow(16,2) + bits[i]
	print("%s: %d"%(tag, dec/div)) #十进制


def PrintfVtxCnt(i, bits):
	"""
    打印顶点的数量
    """
	indx = i + 24   # vertex 数量距离$VTX为24
	if len(bits) > (indx + 3):  # 数量长度是4bit
		Prin4f(indx, "vertex cnt", bits)
	else:
		print("PrintVtxCnt ERR")


def PrinfAddr(start, end, bits):
	#
	#  打印vert&indices地址, face count
	#
    findRsi = False
    for i in range(end - start):
    	if IsDefRsi(i + start, bits):
    		indx =  i + start + 32
    		print("vertex addr: %x%x%x"%(bits[indx+2], bits[indx+1], bits[indx])) 
    		indx = indx + 16
    		print("face   addr: %x%x%x"%(bits[indx+2], bits[indx+1], bits[indx]))
    		indx = indx + 4
    		Prin4f(indx, "face   cnt", bits, 2)
    		findRsi = True
    		break
    if not findRsi:
    	print("not find rsi range %d, %d"%(start, end))


def FindCt0(start, end, bits):
	"""
	在区间内查找结束符
	"""
	for i in range(end - start):
		if IsDefCt0(i + start, bits):
			return i + start
	return 0


def FormatOutput(vtx_list, ct0_list, bits):
	"""
	格式化输出
	"""
	len_list = len(vtx_list)
	for i in range(len_list):
		start  = vtx_list[i]
		end = ct0_list[i]
		print("\n********* %d **********"%i)
		print("start: %x, end: %x"%(start, end))
		PrinfAddr(start, end, bits)
		PrintfVtxCnt(start, bits)
		PrintFVF(start, end, bits)


def parse_binary(bits, length):
	"""
	全局搜索 然后格式化输出
	"""
	vtx_list = []
	ct0_list = []
	for i in range(length):
		if IsDefVtx(i, bits):
			vtx_list.append(i)
	len_list = len(vtx_list)
	for i in range(len_list):
		start = vtx_list[i]
		end = length
		if (i+1) < len_list:
			end = vtx_list[i+1]
		ct0 = FindCt0(start, end, bits)
		if(ct0 > 0 ):
			ct0_list.append(ct0)
		else:
			print("ct0 error, %d %d, %d"%(i, start, end))
	print("mesh count: %d \n"%len(ct0_list))
	FormatOutput(vtx_list, ct0_list, bits)
	
		

def parse_npk(file):
	"""
	解析.npk
	"""
	with open(file, 'rb') as f:
		data = f.read()
		size = f.tell()
		bits = bytearray(data)
		parse_binary(bits, size)


if __name__=='__main__':
	arv= sys.argv
	if( len(arv) > 1):
		file = sys.argv[1]
		parse_npk(file)
	else:
		print("error arg is invalid, please passin .npk file path")
		exit(1)
