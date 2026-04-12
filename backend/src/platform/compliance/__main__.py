"""Allow running compliance gate via: python -m src.platform.compliance.runner"""

import asyncio
from src.platform.compliance.runner import _main

asyncio.run(_main())
