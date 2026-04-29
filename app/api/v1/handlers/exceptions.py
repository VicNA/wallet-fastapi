from fastapi import status


class AppException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "APP_ERROR"

    def __init__(self, message: str):
        self.message = message


class WalletNotFound(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "WALLET_NOT_FOUND"

class WalletNotEnoughFunds(AppException):
    error_code = "WALLET_NOT_ENOUGH_FUND"

class OptimisticLockException(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = "OPTIM_LOCK_ERROR"
