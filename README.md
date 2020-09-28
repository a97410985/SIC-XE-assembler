## 目前組譯器支援的功能
1. 與機器無關的特色
    1. Literals : 
        可以在運算元欄位直接填入字元或數字當值
        ENDFIL    LDA    =C'EOF'   => 值為字元EOF
        WLOOP     TD     =X'05'    => 值為'05'十六進位
        1. LTORG assembler directive : 可以強制將目前收集到的literal pool的內容在此位置存放
    2. Symbol-Defining Statements :
        可以定義自己的符號來代表給某個值，ex: 
        MAXLEN  EQU  4096 => MAXLEN這個符號的值為4096
    3. Expressions :
        使用EQU來定義符號的值時可以使用表達式(表達式的結果必須是絕對的值)，
        ex:
        MAXLEN   EQU   BUFEND-BUFFER
        ex:
        TEST    EQU     5 * 4 + 6 / 2
    4. Program Block : 
        可以使用USE assembler directive來定義目前是哪一個program block，這樣可以在宣告大量記憶體空間時使用另一個program block，讓那些program block被排列在後面，這樣在存取時不會因為距離太遠使用base addressing
2. assembler directive
    1. BASE directive :
        當program-counter相對地址不夠用時就會用base addressing，BASE directive可以定義base的值，之後base addressing就會用加上base的值

## 組譯器的實作簡介
1. 與機器無關的特色
    1. Literals : 
        1. 使用immediate addressing組譯器會把值編進指令的object code中，而Literals則是組譯器會在其他記憶體位置產生值，只儲存跟Literal相差的位址，之後執行時用相差距離取值。
        2. 每個程式區段都會有一個literal pool，重複使用到的literal只需存一個到literal pool，然後literal pool會插在一個程式區段結束的位置
    2. 

## 測試程式說明
1. sic_xe_fig2_9.txt
    就一般SIC/XE的組語，不過還有用Literal、Symbol-Defining、Expression
2. sic_xe_fig2_11.txt
    可以使用program block，有USE assembler directive，可以定義目前是用哪個program block

## 可生出每一行指令的object code
1. sic_xe_fig2_9.txt
2. sic_xe_fig2_11.txt

## 可生出object program
1. sic_xe_fig2_9.txt
2. sic_xe_fig2_11.txt