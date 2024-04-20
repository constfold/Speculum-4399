package unit4399.events
{
    import flash.events.Event;

    public class RankListEvent extends Event
    {

        public static const RANKLIST_ERROR:String = "rankListError";

        public static const RANKLIST_SUCCESS:String = "rankListSuccess";

        protected var _data:Object;

        public function RankListEvent(type:String, dataOb:Object = null, bubbles:Boolean = false, cancelable:Boolean = false)
        {
            super(type, bubbles, cancelable);
            this._data = dataOb;
        }

        public function get data():Object
        {
            return this._data;
        }

        override public function clone():Event
        {
            return new RankListEvent(type, this.data, bubbles, cancelable);
        }
    }
}
