from dataclasses import dataclass


@dataclass
class MotorsBusConfig:
    """Configuration de base pour les bus de moteurs."""
    type: str


@dataclass
class FeetechMotorsBusConfig(MotorsBusConfig):
    """Configuration pour les moteurs Feetech."""
    port: str
    motors: dict[str, tuple[int, str]]
    mock: bool = False

    def __init__(self, port: str, motors: dict[str, tuple[int, str]], mock: bool = False):
        super().__init__(type="feetech")
        self.port = port
        self.motors = motors
        self.mock = mock
