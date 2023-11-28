# Overview
This repository demonstrates a soft IOC based on **ooEpicsPy**. 

# Soft IOC Development Workflow
## Create a Git repository
You need to create a Git repository for your soft IOC. For example:
- Open a Chrome brower and go to address `https://git.xxx/epics_iocboot` (this is only an example, you may put your soft IOC in other suitable locations).
- Create a new project (here use the soft IOC `RCBE` as example).
- Go to your local work folder, like `git_root`, clone the newly created empty repository:
    ```
    cd ~/git_root
    git clone git@git.xxx:epics_iocboot/rcbe.git RCBE
    ```

## Add `ooEpicsPy` as a submodule to your repository
    ```
    cd ~/git_root/RCBE
    git submodule add git@git.xxx:[path of ooEpicsPy]/ooEpicsPy.git Lib/ooEpicsPy
    ```

## Edit source codes for your soft IOC
- The `Service_Log.py` file can be directly reused.
- The `Makefile` can be directly reused.
- Edit `Service_*.py` files as interfaces to communicate with other IOCs.
- Edit `Job_*.py` files to implement functions/procedures of your soft IOC.
- Edit `FSM_*.py` files to implement finite state machines for your soft IOC.
- Edit `Softioc_Top.py` to assemble the components above into a module.
- Edit `Install_SoftIOC.py` with your soft IOC name and the PV name prefix, also change the path for copying `ooEpicsPy` codes.

Note that the files `*_all.subs, *_run.py, *_startup.script, *.template` are generated automatically and please do not edit them. 

## Edit GUI
Edit the panels and store them in the folder `gui`.

## Other Notes:
### When run the test softIOC or open the GUI, first export the EPICS CA address list as:
    ``` 
        export EPICS_CA_ADDR_LIST="${EPICS_CA_ADDR_LIST} localhost"
    ```

# Disclaimer
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



