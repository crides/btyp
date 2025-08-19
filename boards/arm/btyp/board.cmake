# SPDX-License-Identifier: MIT

board_runner_args(pyocd "--target=nrf52840")
include(${ZEPHYR_BASE}/boards/common/pyocd.board.cmake)
