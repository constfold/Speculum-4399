package unit4399.events
{
    import flash.events.Event;

    public class SaveEvent extends Event
    {

        public static const LOG:String = "logreturn";

        public static const SAVE_SET:String = "saveuserdata";

        public static const SAVE_GET:String = "getuserdata";

        public static const SAVE_LIST:String = "getuserdatalist";

        public static const SAVE_LIST_COUNT:String = "getuserdatalistcount";

        protected var _data:Object;

        public function SaveEvent(param1:String, data:Object, bubbles:Boolean = false, cancelable:Boolean = false)
        {
            super(param1, bubbles, cancelable);
            this._data = data;
        }

        public function get ret():Object
        {
            return this._data;
        }

        public function get data():Object
        {
            return this._data;
        }

        override public function toString():String
        {
            return formatToString("DataEvent:", "type", "bubbles", "cancelable", "data");
        }

        override public function clone():Event
        {
            return new SaveEvent(type, this.data, bubbles, cancelable);
        }
    }
}
