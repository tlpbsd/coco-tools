0 REM THIS IS A TEST OF EXPRESSIONS
10 A9 = 10
20 AA = -10
30 AA = -1E+30
40 AA = +1.2345E - 30
50 CC = DD
60 BB = (20)
70 BB = (XX)
80 DD = -(YY)
90 A = 14 * 15
100 X = NOT CC
110 A = 32 * 40 * CC
120 A = (32 - 40) * (CC + 35)
130 A = 32 - 40 / CC * 35 - 25
140 K9 = NOT(CC)
150 K(9) = 32
160 $F = "HELLO"
170 $DD10 = "GOOD" & " bye 128!@#"
180 $DD10 = "GOOD" & $A9
190 A = AA(II + 32) + 32
200 IF A=32 THEN 120
210 A = 32 REM DO SOMETHING
220 :::: A=-1E-64
220 A=-1E-64 : REM HERE
230 IF AA=32 THEN 20
240 IF (BB AND 74) THEN BB = 32
250 IF (BB AND 74) THEN 20 ELSE 50
260 IF B9=B(9) THEN 20 ELSE B=100
270 IF B9=B9 THEN A=2 ELSE B=123
280 IF B=1 THEN A=3:B=10 ELSE C=20
290 IF B=1 THEN A=3:B=10 ELSE IF C=20 THEN D=D+1