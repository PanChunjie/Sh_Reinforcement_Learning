using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using VISSIMLIB;
using Microsoft.Office.Interop.Excel;
using System.Reflection;
using System.IO;

namespace ConsoleApplication1
{
    class VehInfo
    {
        private int sid;
        private int vid;
        private int typ;
        private int lnk;
        private int lan;
        private double loc;
        private double spd;
        private double len;
        private double gap;
        private double crtTime;
        private double crtLoc;
        private int rel_vid; // onramp <-> mainline vehicle
        public int Sid { get { return sid; } set { sid = value; } }
        public int Vid { get { return vid; } set { vid = value; } }
        public int Vid_rel { get { return rel_vid; } set { rel_vid = value; } }
        public int Typ { get { return typ; } set { typ = value; } }
        public int Lnk { get { return lnk; } set { lnk = value; } }
        public int Lan { get { return lan; } set { lan = value; } }
        public double Loc { get { return loc; } set { loc = value; } }
        public double Spd { get { return spd; } set { spd = value; } }
        public double Len { get { return len; } set { len = value; } }
        public double Gap { get { return gap; } set { gap = value; } }
        public double CrtTime { get { return crtTime; } set { crtTime = value; } }
        public double CrtLoc { get { return crtLoc; } set { crtLoc = value; } }
    }

    class Vissim
    {







        //Print out Info
        // VissimTools.AllLinksInfo();
        //  VissimTools.AllVehiclesName();
        //  VissimTools.Get_DetectorName();


    }

    class VissimTools
    {

        #region Initial Values

        public const string NetworkPath = @"D:\School11111111111111111111111111111\Coop2019\Summer\Vissim 2\SH.inpx";
        public const string LayoutPath = @"D:\School11111111111111111111111111111\Coop2019\Summer\Vissim 2\SH.layx";
        //Simulation time in seconds
        public const int SimPeriod = 18000;
        // This represents how many times the Vissim traffic model runs in a second during the simulation.
        public static int SimRes = 5;
        public static int RandSeed = 54;
        public static int DataCollectionInterval = 180; //3 mins

        #endregion
           

          
        public static VISSIMLIB.Vissim vissim = new VISSIMLIB.Vissim();
        //public static IDataCollectionMeasurementContainer datapoints = vissim.Net.DataCollectionMeasurements;

        #region Basic Function

        public static void InitVissimTools()
        {
            //Load a Network
            vissim.LoadNet(NetworkPath);
            //Load a Layout
            vissim.LoadLayout(LayoutPath);    
            vissim.SuspendUpdateGUI();
            SetSimulationAtts(SimPeriod, SimRes, RandSeed);
            SetEvaluationAtts(SimPeriod, DataCollectionInterval);
            vissim.ResumeUpdateGUI();

        }

        public static void SetSimulationAtts(int simPeriod, int simRes, int randSeed)
        {
            //  vissim.Net.Evaluation.AttValue["DataCollToTime"] = simperiod;
            //   vissim.Net.Evaluation.AttValue["DataCollInterval"] = 300;

            vissim.Simulation.set_AttValue("simPeriod", simPeriod);
            vissim.Simulation.set_AttValue("simRes", simRes);
            vissim.Simulation.set_AttValue("randSeed", randSeed);
            vissim.Simulation.set_AttValue("NumCores", 1);
            // vissim.Simulation.set_AttValue("UseMaxSimSpeed", true);
            // vissim.Graphics.CurrentNetworkWindow.set_AttValue("QuickMode", 1); //Disable the visibility of all dynamic elements
        }

        public static void SetEvaluationAtts(int simPeriod, int dataCollectionInterval = 30)
        {
            vissim.Evaluation.set_AttValue("DataCollCollectData", true);
            vissim.Evaluation.set_AttValue("DataCollToTime", simPeriod);
            vissim.Evaluation.set_AttValue("DataCollFromTime", 0);
            vissim.Evaluation.set_AttValue("DataCollInterval", dataCollectionInterval);

            vissim.Evaluation.set_AttValue("VehTravTmsCollectData", true);
            vissim.Evaluation.set_AttValue("VehTravTmsToTime", simPeriod);
            vissim.Evaluation.set_AttValue("VehTravTmsFromTime", 0);
            vissim.Evaluation.set_AttValue("VehTravTmsInterval", dataCollectionInterval);

            vissim.Evaluation.set_AttValue("VehNetPerfCollectData", true);
            vissim.Evaluation.set_AttValue("VehNetPerfToTime", simPeriod);
            vissim.Evaluation.set_AttValue("VehRecFromTime", 0);
            vissim.Evaluation.set_AttValue("VehNetPerfInterval", dataCollectionInterval);

            vissim.Evaluation.set_AttValue("KeepPrevResults", "KeepCurrent");
        }

        public static void RunSingleStep()
        {
            vissim.Simulation.RunSingleStep();
        }

        public static void RunContinuous()
        {
            vissim.Simulation.RunContinuous();
        }

        public static double SimulationSecond()
        {
            //end is 0  singlesteptime = 1/simres
            return vissim.Simulation.SimulationSecond;
        }

        public static void Stop()
        {
            vissim.Simulation.Stop();
        }

        public static void saveToExcel(int index, int volume, int vehs)
        {
            string FilePath = "D:/School11111111111111111111111111111/Coop2019/Summer/ConsoleApplication1/ConsoleApplication1/data.xls";
            Application app = new Application { Visible = false };
            FileInfo fi = new FileInfo(FilePath);
            Workbook xBook;
            if (fi.Exists)     //判断文件是否已经存在,如果存在就删除!
            {
                xBook = app.Workbooks.Open(@"D:/School11111111111111111111111111111/Coop2019/Summer/Vissim 2/Data/data.xls");
            }
            else
            {
                xBook = app.Workbooks.Add(Missing.Value);
            }

            Worksheet xSheet = (Worksheet)xBook.Sheets[1];
            string range3 = "A" + index.ToString();
            string range4 = "B" + index.ToString();
            Range rng3 = xSheet.get_Range(range3);
            rng3.Value2 = volume;
            Range rng4 = xSheet.get_Range(range4);
            rng4.Value2 = vehs;

            xBook.SaveAs("D:/School11111111111111111111111111111/Coop2019/Summer/Vissim 2/Data/data.xls", true);
            app.Quit();


        }

        public static void Set_AllDesireSpeed(int speed)
        {
            bool check = vissim.Net.DesSpeedDecisions == null;
            int spd_no = get_DesireSpeedNumer(speed);
            vissim.Net.DesSpeedDecisions.get_ItemByKey(1).set_AttValue("DesSpeedDistr(10)", spd_no); // car
            vissim.Net.DesSpeedDecisions.get_ItemByKey(2).set_AttValue("DesSpeedDistr(10)", spd_no);
            vissim.Net.DesSpeedDecisions.get_ItemByKey(3).set_AttValue("DesSpeedDistr(10)", spd_no);
            vissim.Net.DesSpeedDecisions.get_ItemByKey(1).set_AttValue("DesSpeedDistr(70)", spd_no); // cav
            vissim.Net.DesSpeedDecisions.get_ItemByKey(2).set_AttValue("DesSpeedDistr(70)", spd_no);
            vissim.Net.DesSpeedDecisions.get_ItemByKey(3).set_AttValue("DesSpeedDistr(70)", spd_no);
        }

        public static int get_DesireSpeedNumer(int speed)
        {
            int speednum = 0;
            switch (speed)
            {
                case 30:
                    speednum = 700;
                    break;
                case 35:
                    speednum = 705;
                    break;
                case 40:
                    speednum = 710;
                    break;
                case 45:
                    speednum = 715;
                    break;
                case 50:
                    speednum = 720;
                    break;
                case 55:
                    speednum = 725;
                    break;
                case 60:
                    speednum = 730;
                    break;
                case 65:
                    speednum = 735;
                    break;
                case 70:
                    speednum = 740;
                    break;
                case 75:
                    speednum = 745;
                    break;
                case 80:
                    speednum = 750;
                    break;
                case 85:
                    speednum = 755;
                    break;
                case 90:
                    speednum = 760;
                    break;
                case 95:
                    speednum = 765;
                    break;
                case 100:
                    speednum = 770;
                    break;
                case 104:
                    speednum = 775;
                    break;
                case 110:
                    speednum = 780;
                    break;
                case 115:
                    speednum = 785;
                    break;
                case 120:
                    speednum = 790;
                    break;
            }
            return speednum;
        }

        //Provide initial state(flowrate) to agent
        // TODO: Add density to initial state for further consideration
        // TODO: Double check the implementation are flowrate and discharging rate
        public static double vissimState(int run_times, int action = 104) //SimPeriod * SimRes
        {
            Set_AllDesireSpeed(action);       
            double flowrate = 0;
            for (int i = 0; i < run_times; i++)
            {
                VissimTools.RunSingleStep();             
                
            }
            int datapoint1_vehs = VissimTools.Get_CurrentDataCollectionResult_Vehs(1);
            //int num_lanes = VissimTools.Get_NumLaneByVehTravelTm(2);
            flowrate = VissimTools.Get_FlowRate(datapoint1_vehs, DataCollectionInterval);
            // int density = VissimTools.Get_Density(int num_vehs, int timeinterval, double speed, double distance, int num_lane)
            return flowrate;
        }
        public static double vissimReward(int run_times, int action) //SimPeriod * SimRes
        {
            Set_AllDesireSpeed(action);
            double Reward = 0;
            for (int i = 0; i < run_times; i++)
            {
                VissimTools.RunSingleStep();
            }        
            int datapoint1_vehs = VissimTools.Get_CurrentDataCollectionResult_Vehs(4);
            Reward = VissimTools.Get_FlowRate(datapoint1_vehs, DataCollectionInterval);
            // int density = VissimTools.Get_Density(int num_vehs, int timeinterval, double speed, double distance, int num_lane)
            return Reward;
        }



        #endregion


        //var vI = VissimTools.vissim.Net.VehicleInputs;
        //vI.get_ItemByKey(1).set_AttValue("Volume(1)", 3000 + K * 1000);
        //VissimTools.RunContinuous();
        //int num_vehs =  VissimTools.Get_VehicleTravelTime_Vehs(4, "Total");
        //VissimTools.saveToExcel(K + 1, 3000 + K * 1000, num_vehs);

        // GC.Collect();
        //         VissimTools.Stop();





        #region Detectors
        static public bool Get_DetectorPresence(string detectorId)
        {
            return System.Convert.ToBoolean(vissim.Net.Detectors.get_ItemByKey(detectorId).get_AttValue("Presence"));

        }

        static public double Get_DetectorSpeed(string detectorId)
        {
            return System.Convert.ToDouble(vissim.Net.Detectors.get_ItemByKey(detectorId).get_AttValue("VehSpeed"));
        }
        static public void Get_DetectorName()
        {
            //return Convert.ToDouble(vissim.Net.Detectors.get_ItemByKey(detectorId).get_AttValue("Name"));
            var detectors = VissimTools.vissim.Net.Detectors.GetAll();
            System.Console.WriteLine("No:  ；  " + detectors[0].AttValue["No"] + " Name:  ；  " + detectors[0].AttValue["Name"]);
            System.Console.WriteLine("No:  ；  " + detectors[1].AttValue["No"] + " Name:  ；  " + detectors[1].AttValue["Name"]);
        }
        #endregion

        #region Single Vehicle Info
        static public IVehicle Get_Veh(int vid) { return vissim.Net.Vehicles.get_ItemByKey(vid); }
        static public int Get_VehType(int vid) { return int.Parse(vissim.Net.Vehicles.get_ItemByKey(vid).get_AttValue("VehType").ToString()); }
        static public double Get_VehSpd(int vid) { return System.Convert.ToDouble(vissim.Net.Vehicles.get_ItemByKey(vid).get_AttValue("Speed")); }
        static public double Get_VehPos(int vid) { return System.Convert.ToDouble(vissim.Net.Vehicles.get_ItemByKey(vid).get_AttValue("Pos")); }
        static public double Get_VehAcc(int vid) { return System.Convert.ToDouble(vissim.Net.Vehicles.get_ItemByKey(vid).get_AttValue("Acceleration")); }
        static public double Get_VehLateral(int vid) { return System.Convert.ToDouble(vissim.Net.Vehicles.get_ItemByKey(vid).get_AttValue("PosLat")); }
        public static int GetNextLink(int vid) { return int.Parse(vissim.Net.Vehicles.get_ItemByKey(vid).get_AttValue("NextLink").ToString()); }
        #endregion

        #region All Vehicle Info
        public static void AllLinksInfo()
        {
            //Print out Link Info
            foreach (ILink link in vissim.Net.Links)
            {
                Int32 linkNumber = (Int32)link.AttValue["No"];
                string linkName = (string)link.AttValue["Name"];
                System.Console.WriteLine("Link" + linkNumber + "(" + linkName + ")");
            }
        }

        public static void AllVehiclesInfo()
        {
            //Print out Vehicle Input Info
            foreach (IVehicleInput vehicleInput in vissim.Net.VehicleInputs)
            {
                int vehicleInputNumber = vehicleInput.AttValue["No"];
                string vehicleInputLink = vehicleInput.AttValue["Link"];
                System.Console.WriteLine("Vehicle No: " + vehicleInputNumber + "  VehicleInputLink: " + vehicleInputLink + "");
            }
        }
        public static void AllVehiclesName()
        {
            var names = VissimTools.vissim.Net.VehicleInputs.GetMultiAttValues("No");
            foreach (int name in names)
            {
                System.Console.WriteLine("Vehicle No11: " + name);
            }
        }
        public static object GetAllVehiclesByID() { return ConsoleApplication1.VissimTools.vissim.Net.Vehicles.GetMultiAttValues("No"); }
        public static object GetAllVehiclesByType() { return VissimTools.vissim.Net.Vehicles.GetMultiAttValues("VehType"); }
        public static object GetAllVehiclesByLane() { return VissimTools.vissim.Net.Vehicles.GetMultiAttValues("Lane"); }
        public static object GetAllVehiclesByLink() { return VissimTools.vissim.Net.Vehicles.GetMultiAttValues("Link"); }
        public static object GetAllVehiclesByPos() { return VissimTools.vissim.Net.Vehicles.GetMultiAttValues("Pos"); }
        public static object GetAllVehiclesByLanes(int LinkKey, int LanesKey) { return vissim.Net.Links.get_ItemByKey(LinkKey).Lanes.get_ItemByKey(LanesKey).Vehs; }// ????
        #endregion

        #region LinkInfo
        public static object GetLinkIDs() { return VissimTools.vissim.Net.Links.GetMultiAttValues("No"); }
        public static object GetLinksTotalLanes() { return VissimTools.vissim.Net.Links.GetMultiAttValues("NUMLANES"); }
        public static object GetLinkVehiclesbyNumber(int lkn) { return vissim.Net.Links.get_ItemByKey(lkn).Vehs.GetMultiAttValues("No"); } // OK
        public static object GetLinkVehiclesByType(int lkn) { return vissim.Net.Links.get_ItemByKey(lkn).Vehs.GetMultiAttValues("VehType"); } // OK
        public static int Get_NumLaneByVehTravelTm(int vttId)
        {
            switch (vttId)
            {
                case 1:
                    return vissim.Net.Links.get_ItemByKey(6).get_AttValue("NumLanes");
                    break;
                case 2:
                    return vissim.Net.Links.get_ItemByKey(3).get_AttValue("NumLanes");
                    break;
                case 3:
                    return vissim.Net.Links.get_ItemByKey(3).get_AttValue("NumLanes");
                    break;
            }
            return 0;
        }

        #endregion

        #region Data Collection Result
        static public int Get_CurrentDataCollectionResult_Vehs(int dcId)
        {
            var datapoints = vissim.Net.DataCollectionMeasurements;
            return datapoints.get_ItemByKey(dcId).get_AttValue("Vehs(Current, Last, All)");
        }
        static public double Get_CurrentDataCollectionResult_SpeedAvgArith(int dcId)
        {
            var datapoints = vissim.Net.DataCollectionMeasurements;
            return Convert.ToDouble(datapoints.get_ItemByKey(dcId).get_AttValue("SpeedAvgArith(Current, Last, All)"));
        }
        static public int Get_CurrentDataCollectionResult_TravTm(int dcId)
        {
            var datapoints = vissim.Net.DataCollectionMeasurements;
            return datapoints.get_ItemByKey(dcId).get_AttValue("Vehs(Current, Last, All)");
        }
        static public int Get_DataCollectionResult_Vehs(int dcId, string timeInterval)
        {
            var datapoints = vissim.Net.DataCollectionMeasurements;
            string attribute = "Vehs(Current," + timeInterval + ", All)";
            return datapoints.get_ItemByKey(dcId).get_AttValue(attribute);
        }
        static public double Get_DataCollectionResult_SpeedAvgArith(int dcId, string timeInterval)
        {
            var datapoints = vissim.Net.DataCollectionMeasurements;
            string attribute = "SpeedAvgArith(Current," + timeInterval + ", All)";
            return Convert.ToDouble(datapoints.get_ItemByKey(dcId).get_AttValue(attribute));
        }

        #endregion

        #region Vehicle Travel Time Result
        static public int Get_CurrentVehicleTravelTime_Vehs(int vttId)
        {
            var traveltimes = vissim.Net.VehicleTravelTimeMeasurements;
            return traveltimes.get_ItemByKey(vttId).get_AttValue("Vehs(Current, Last, All)");
        }
        static public int Get_CurrentVehicleTravelTime_TravTm(int vttId)
        {
            var traveltimes = vissim.Net.VehicleTravelTimeMeasurements;
            return traveltimes.get_ItemByKey(vttId).get_AttValue("TravTm(Current, Last, All)");
        }
        static public double Get_CurrentVehicleTravelTime_DistTrav(int vttId)
        {
            var traveltimes = vissim.Net.VehicleTravelTimeMeasurements;
            return Convert.ToDouble(traveltimes.get_ItemByKey(vttId).get_AttValue("DistTrav(Current, Last, All)"));
        }
        static public int Get_VehicleTravelTime_Vehs(int vttId, string timeInterval)
        {
            var traveltimes = vissim.Net.VehicleTravelTimeMeasurements;
            string attribute = "Vehs(Current," + timeInterval + ", All)";
            return traveltimes.get_ItemByKey(vttId).get_AttValue(attribute);
        }
        static public int Get_VehicleTravelTime_TravTm(int vttId, string timeInterval)
        {
            var traveltimes = vissim.Net.VehicleTravelTimeMeasurements;
            string attribute = "TravTm(Current," + timeInterval + ", All)";
            return traveltimes.get_ItemByKey(vttId).get_AttValue(attribute);
        }
        static public double Get_VehicleTravelTime_DistTrav(int vttId, string timeInterval)
        {
            var traveltimes = vissim.Net.VehicleTravelTimeMeasurements;
            string attribute = "DistTrav(Current," + timeInterval + ", All)";
            return Convert.ToDouble(traveltimes.get_ItemByKey(vttId).get_AttValue(attribute));
        }
        static public double Get_VehicleTravelTime_Dist(int vttId)
        {
            var traveltimes = vissim.Net.VehicleTravelTimeMeasurements;
            return Convert.ToDouble(traveltimes.get_ItemByKey(vttId).get_AttValue("Dist"));
        }
        #endregion

        #region calculation
        static public double Get_Link_Desity(int lnk)
        {
            double length = System.Convert.ToDouble(vissim.Net.Links.get_ItemByKey(lnk).get_AttValue("Length2D"));
            int num_lanes = System.Convert.ToInt32(vissim.Net.Links.get_ItemByKey(lnk).get_AttValue("NumLanes"));
            object[,] temp = (object[,])VissimTools.GetLinkVehiclesbyNumber(lnk);
            int num_vehs = temp.Length / 2;
            double density = num_vehs / (num_lanes * length / 1600); //  veh/mi/ln
            return Math.Round(density, 0);

        }
        static public double Get_FlowRate(int num_vehs, int timeinterval)
        {

            double flowrate = num_vehs * (3600.0 / timeinterval); //  veh/h
            return flowrate;
        }
        static public double Get_Density(int num_vehs, int timeinterval, double speed, double distance, int num_lane)
        {

            double flowrate = num_vehs * (3600.0 / timeinterval); //  veh/h
            double velocity = distance / speed;
            double density = flowrate / (num_lane * velocity);
            return Math.Round(density, 0);
        }

        #endregion

    }
}
