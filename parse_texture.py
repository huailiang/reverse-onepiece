#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Author: penghuailiang
# @Date  : 2019-08-15


import os
import sys
import re

from PIL import Image

npk_file = ""
npkv_file = ""
out_dir = ""

def IsDefTxr(i, bits): 
	"""
	查找结束$TXR
    """
	if i > len(bits)-4:  
		return False
	if bits[i] == 36 and bits[i+1] == 84 and bits[i+2] == 88 and bits[i+3] == 82:
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



def FindCt0(start, end, bits):
	"""
	在区间内查找结束符
	"""
	for i in range(end - start):
		if IsDefCt0(i + start, bits):
			return i + start
	return 0


def FindRsi(start, end, bits):
	for i in range(end - start):
		if IsDefRsi(i + start, bits):
			return i + start
	return 0


def GetImgFmt(fmt):
	fmtr = ""
	arg = 0
	bytespp = 0
	if fmt == 0x0F:
		fmtr = "DXT1"
		arg = 1 
		bytespp = 8
	elif fmt == 0x11:
		fmtr = "DXT5"
		arg = 3
		bytespp = 16
	elif fmt == 0x14:
		fmtr = "BC5"
		arg = 5
		bytespp = 16
	elif fmt == 0x16:
		fmtr = "BC4"
		arg     = 4
		bytespp = 8
	return (fmtr, arg, bytespp)


def PrintImageInfo(start, bits):
	indx = start + 16 + 4
	swiz = bits[indx+1] * 16**2 + bits[indx]
	indx +=  2
	width = bits[indx+1] * pow(16, 2) + bits[indx]
	indx += 2
	height = bits[indx + 1] * pow(16, 2) + bits[indx]
	indx += 2
	scanline = bits[indx + 1] * pow(16, 2) + bits[indx]
	indx += 2
	fmt = bits[indx]
	(fmtr, arg, bytespp) = GetImgFmt(fmt)
	print("size:(%dx%d) scanline:%d fmtr: fmt:0x%02x(%s)"%(width, height, scanline, fmt, fmtr))
	return (width, height, scanline, fmt, arg, bytespp)


def FormatOutput(txr_list, ct0_list, bits):
	"""
	格式化输出
	"""
	len_list = len(txr_list)
	for i in range(len_list):
		start  = txr_list[i]
		end = ct0_list[i]
		indx = FindRsi(start, end, bits)
		mip = indx + 3 + 16
		v_mip = bits[mip]
		iname = indx + 16 * (v_mip + 2)
		names = ""
		for j in range(32):
			names += chr(bits[iname+j])
			if(bits[iname+j] == 0):
				break
		print("%d texture name:%s\tmipmap:%d"%(i, names, v_mip))
		(width, height, scanline, fmt, arg, bytespp) = PrintImageInfo(start, bits)
		for j in range(v_mip):
			i_mip = indx + 16 * (j + 2)
			h_addr = bits[i_mip+3] * 16**6 + bits[i_mip+2] * 16**4 + bits[i_mip+1] * 16**2 + bits[i_mip] 
			h_addr = h_addr & 0x0FFFFFFF
			i_len = i_mip + 4
			c_len = bits[i_len+3] * 16**6 + bits[i_len+2] * 16**4 + bits[i_len+1] * 16**2 + bits[i_len] 
			print(" - %02d, addr:0x%08x \tlength: %d"%(j, h_addr, c_len))
			if j == 0:
				save_img(names, width, height, h_addr,c_len, fmt, arg, bytespp)
				break


def save_img(name, width, height, mipmap_start, mipmap_len, fmt, arg, bytespp):
	
	if npkv_file=="":
		print(" npkv_file is empty")
		return
	if fmt not in [0x0F, 0x11, 0x14, 0x16, 0x1C]:
		return
	if width<=4 or height <= 4:
		return
	imname = npkv_file
	with open(imname) as f:
		f.seek(mipmap_start)
		img_data = bytearray(f.read(mipmap_len))
		decoder = "bcn"
		mode = "RGBA"
        # print(" %4d %4d 0x%08X 0x%08X" % ( width, height, mipmap_start, mipmap_len))
        img = Image.frombytes(mode, (width, height), bytes(img_data), decoder, arg)
        # img.show()
        img.save(out_dir+name.split('.')[0]+".png")


def parse_binary(bits, length):
	"""
	全局搜索 然后格式化输出
	"""
	txr_list = []
	ct0_list = []
	for i in range(length):
		if IsDefTxr(i, bits):
			txr_list.append(i)
	len_list = len(txr_list)
	for i in range(len_list):
		start = txr_list[i]
		end = length
		if (i+1) < len_list:
			end = txr_list[i+1]
		ct0 = FindCt0(start, end, bits)
		if(ct0 > 0 ):
			ct0_list.append(ct0)
		else:
			print("ct0 error, %d %d, %d"%(i, start, end))
	print("texture count: %d \n"%len(ct0_list))
	FormatOutput(txr_list, ct0_list, bits)
	
	

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
	if ( len(arv) > 3 ):
		out_dir = sys.argv[3]
		npkv_file = sys.argv[2]
		npk_file = sys.argv[1]
		if not os.path.exists(out_dir):
			print("error: output directory is not exists")
		elif not os.path.exists(npk_file):
			print("error: npk file is invalid")
		elif not os.path.exists(npkv_file):
			print("error: npkv file is invalid")
		else:
			parse_npk(npk_file)
	else:
		print("error: arg is invalid, $1:.npk file path, $2: npkv file path, $3: output directory")
		exit(1)
