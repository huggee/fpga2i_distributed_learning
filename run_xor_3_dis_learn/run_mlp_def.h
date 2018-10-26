#include <SPI.h>
#include <SpiRAM.h>

const uint32_t ramSize = 0x1FFFF;           // 128K x 8 bit
const byte LED = 13;

#define SRAM0 0x100000 // SRAM0の先頭アドレス
#define SRAM1 0x200000 // SRAM1の先頭アドレス

#define GPIO0 0x00
#define GPIO1 0x04
#define GPIO2 0x08
#define GPIO3 0x0c
#define GPIO4 0x10
#define GPIO5 0x14
#define GPIO6 0x18
#define GPIO7 0x1c

#define N_IN 4
#define N_H 30
#define N_OUT 2

#define N_WH N_IN * N_H
#define N_WO N_H * N_OUT

// 初期化データの総数
#define N_DATA_0 N_WH + N_WO + N_IN + N_OUT + N_OUT
#define N_DATA_1 N_WH + N_WO

#define ADDR_WH_START     0
#define ADDR_WO_START     ADDR_WH_START + N_WH  // 隠れ-出力層の重み開始アドレス
#define ADDR_INPUT_START  ADDR_WO_START + N_WO    // 入力データ開始アドレス
#define ADDR_LABEL_START  ADDR_INPUT_START + N_IN
#define ADDR_OUTPUT_START ADDR_LABEL_START + N_OUT

#define ADDR_WH_END      ADDR_WO_START - 1
#define ADDR_WO_END      ADDR_INPUT_START - 1
#define ADDR_INPUT_END   ADDR_LABEL_START - 1
#define ADDR_LABEL_END  ADDR_OUTPUT_START - 1
#define ADDR_OUTPUT_END ADDR_OUTPUT_START + N_OUT - 1

void sram_data_init(SpiRAM);
void sram_wait_init(SpiRAM);

void wait_ack(SpiRAM, byte);


void send_operation(SpiRAM, byte);
void print_recieved_data(SpiRAM);

void zero_filling(SpiRAM);

void run_neural_network(SpiRAM, byte);
