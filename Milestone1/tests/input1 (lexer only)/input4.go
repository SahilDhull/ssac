// run

// Copyright 2009 The Go Authors. All rights reserved.
// Use of this source code is governed by a BSD-style
// license that can be found in the LICENSE "file."

// Test literal syntax for basic types.

package main

var nbad int

func main() {
	// bool
	var t bool = true
	var f bool = false


	// int64
	var i30 int64 = 0
	var i31 int64 = 1
	var i32 int64 = -1
	var i33 int64 = 0600  //600
	var i34 int64 = 0xBadFace  /*HEXADECIMAL*/
	var i35 int64 = -9223372036854775808
	var i36 int64 = +9223372036854775807
	_, _, _, _ = i30, i31, i32, i33

	// float
	var f00 float32 = 3.14159
	var f01 float32 = -3.14159
	var f03 float32 = 0.0
	var f04 float32 = .0
	var f05 float32 = 0.
	var f06 float32 = -0.0
	var f07 float32 = 072.40   // == 72.40
	var f09 float32 = 1e-10
	var f10 float32 = 1e+10
	var f11 float32 = 6.67428e-11
	var f13 float32 = .1e-10
	var f14 float32 = .1e+10
	var f15 float32 = 1E6
	var f16 float32 = 0i
	var f16 float32 = 0.1i
	var f16 float32 = 6.67428e-11i
	var f16 float32 = 1E6i
	var f16 float32 = .12345E+5i


	// string
	var s0 string = ""
	var s1 string = "hello"
	var s2 string = "\a\b\f\n\r\t\v"
	_, _ = s0, s2

	var s00 string = "\000 & * () $ # \n"
	var s01 string = "\007"
	var s02 string = "\377"

	var x00 string = "\x00"
	var x01 string = "\x0f"
	var x02 string = "\xff"

	if nbad > 0 {
		panic("literal failed")
	}
}
