# ooEpicsPy
`ooEpicsPy` is a Python version of `ooEpics` (https://github.com/aaqiao/ooEpics) aiming at developing soft IOCs. Base classes are provided to skeleton EPICS soft IOCs, mainly or middle-layer application servers. `ooEpicsPy` provides the following features:
- EPICS database can be created by creating objects of `LocalPV`s in the user code.
- Basic Channel Access functions (e.g. `caget`, `caput`, `camonitor`, w/o callbacks …) are wrapped by the `RemotePV` class based on the `PyEpics` module. 
- Provides base classes to implement finite state machines.
- Provides an active `Application` class to execute user command driven jobs.
- Provides an example soft IOC code in the folder `example`.

## Dependencies
`ooEpicsPy` depends on the following non-standard Python modules:
- PyEpics: https://pyepics.github.io/pyepics/

## Disclaimer (see the **LICENSE** file)
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

