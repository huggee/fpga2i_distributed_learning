#include <SPI.h>
#include <SpiRAM.h>
#include "run_mlp_def.h"

void sram_data_init(SpiRAM sRam){
    uint32_t i = 0;
    byte x0, x1;
    byte buffer[10] = {};

    x0 = B00000000;
    x1 = B00100000;

    for(i = ADDR_INPUT_START; i <= ADDR_INPUT_END; i++){
        sRam.readBuffer(SRAM0 + i, (char *)buffer, 1);
        Serial.print(i, HEX);
        Serial.print(", ");
        Serial.print(buffer[0], HEX);
        Serial.println("");
    }

    for(i = ADDR_LABEL_START; i <= ADDR_LABEL_END; i++){
        sRam.readBuffer(SRAM0 + i, (char *)buffer, 1);
        Serial.print(i, HEX);
        Serial.print(", ");
        Serial.print(buffer[0], HEX);
        Serial.println("");
    }
}





void sram_wait_init(SpiRAM sRam){
    uint32_t i = 0;
    int randNum_0;
    byte randbit_0;
    byte randbit_1;
    byte buffer[10] = {};

    for(i = 0; i <= ADDR_LABEL_END; i++){
        if(i <= ADDR_WH_END){
            randNum_0 = random(0, 256);
            //randbit_0 = (randNum_0 % 64) + ((( (randNum_0 >> 5) % 2) * 3) << 6);
            randbit_0 = randNum_0;
            randbit_1 = random(0, 256);

            sRam.writeBuffer(SRAM0 + i, (char *)&randbit_0, 1);
            sRam.writeBuffer(SRAM1 + i, (char *)&randbit_1, 1);
        }
        else if(i <= ADDR_WO_END){
          randNum_0 = random(0, 256);
          //randbit_0 = (randNum_0 % 64) + ((( (randNum_0 >> 5) % 2) * 3) << 6); // -1 to +1
          randbit_0 = randNum_0; // -4 to +4
          randbit_1 = random(0, 256);

          sRam.writeBuffer(SRAM0 + i, (char *)&randbit_0, 1);
          sRam.writeBuffer(SRAM1 + i, (char *)&randbit_1, 1);
        }
    }
}

void wait_ack(SpiRAM sRam, byte flag){
    byte buffer[4] = {};

    sRam.readBuffer(GPIO1, (char *)buffer, 4);
    while(buffer[3] != flag){
        sRam.readBuffer(GPIO1, (char *)buffer, 4);
    }
}


void send_operation(SpiRAM sRam, byte op){
    byte buffer[4];

    buffer[0] = 0x00;
    buffer[1] = 0x00;
    buffer[2] = 0x00;
    buffer[3] = op;
    sRam.writeBuffer(GPIO0, (char *)buffer, 4);
}

void print_recieved_data(SpiRAM sRam){
    byte buffer[50];
    int i;
    float value;

    // Serial.print("GPIO ");
    // for(i=0; i<8; i++){
    //     sRam.readBuffer(i*4, buffer, 4);
    //     Serial.print("["); Serial.print(i, DEC); Serial.print("] ");
    //     Serial.print(buffer[0], HEX); Serial.print(" ");
    //     Serial.print(buffer[1], HEX); Serial.print(" ");
    //     Serial.print(buffer[2], HEX); Serial.print(" ");
    //     Serial.print(buffer[3], HEX); Serial.print("  ");
    // }
    /********* 出力結果表示 *********/
    Serial.print(":  "); //Serial.print(SRAM0 + ADDR_OUTPUT_START, HEX); Serial.print(" ");
    sRam.readBuffer(SRAM0 + ADDR_OUTPUT_START, (char *)buffer, N_OUT);
    //value = float(buffer[0]/32.0);
    Serial.print(buffer[0]/32.0);
    // for(i = 0; i < N_OUT; i++){
    //     Serial.print(buffer[i], DEC); Serial.print(" ");
    // }

}


void zero_filling(SpiRAM sRam){
    uint32_t i = 0;
    byte buffer[4];
    byte x0 = 0x00;

    for(i=0; i<8; i++){
        buffer[0] = 0x00;
        buffer[1] = 0x00;
        buffer[2] = 0x00;
        buffer[3] = 0x00;
        sRam.writeBuffer(i*4, (char *)buffer, 4);
    }


    for(i = 0; i <= ramSize; i++){
        sRam.writeBuffer(SRAM0 + i, (char *)&x0, 1);
        sRam.writeBuffer(SRAM1 + i, (char *)&x0, 1);
    }
}
void run_neural_network(SpiRAM sRam, byte mode){
    byte op, flag;

    /********** リセット信号書き込み          **********/
    op = 0x10;
    send_operation(sRam, op);

    /********** FPGAコアのリセット完了まで待つ **********/
    flag = 0x10;
    wait_ack(sRam, flag);

    /********** 実行命令書き込み              **********/
    op = mode;
    send_operation(sRam, op);
    //Serial.print("OP "); Serial.print(op, HEX); Serial.print(": ");

    /********** 実行完了まで待つ              **********/
    flag = 0x0f;
    wait_ack(sRam, flag);
}
