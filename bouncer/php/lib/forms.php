<?php
/**
 *	Form functions for handling form input, output, and markup.
 *	@package mirror 
 *	@subpackage lib
 */

/**
 *	Cleans a string or an array of strings for HTML presentation.
 *	@param mixed $str dirty
 *  @param bool $slashes default to false, this parameter indicate if stripslashes is desired, usually use for magic qoutes
 *	@return mixed $str cleaned for HTML
 */
function clean_out($str, $slashes=FALSE) 
{ 
	if (is_array($str))
	{
		foreach ($str as $key => $val)
		{
			$str[$key] =& clean_out($val, $slashes);
		}
	}
	else
	{
		if ($slashes)
			$str =& trim(htmlentities(stripslashes($str)));
		else
			$str =& trim(htmlentities($str));
	}
	
	return $str;
}

/**
 *	Cleans a string or an array of strings for DB input. 
 *	@param mixed $str dirty
 *  @param bool $single_quote add single quotes around the string, optional
 *  @param bool $decode run html_entity_decode(), optional
 *	@return mixed $ret slashes added, if necessary
 */
function clean_in($str, $single_quotes=FALSE, $decode=FALSE) 
{
	if (is_array($str))
	{
		foreach ($str as $key => $val)
		{
			$str[$key] =& clean_in($val, $single_quotes);
		}
	}
	else
	{
		if (get_magic_quotes_gpc() === 1)
		{
			$str =& trim($str);
		}
		else                                                                            
		{
			$str =& addslashes(trim($str));
		}
		if ($single_quotes) {
			$str = "'" . $str . "'";
		}
		if ($decode) {
			html_entity_decode($str);
		}
	}
	return $str;
}

/**
 *	Get calendar days in array format.
 *  @param int $month numeric representation of month (optional) default is empty, accepted range value is 1-12 inclusive, this affects the total number of days in given month
 *  @param int $year the year (optional) default is empty, this affects the total number of days in given month
 *	@return array $days days from 1->[28-31] (zero-filled)
 */
function array_days($month='',$year='')
{
	$days = Array();
	$num = 1;
	
	// get total number of days of a particular month if given a month and year
	if (!empty($month) && !empty($year) && is_numeric($month) 
		&& is_numeric($year) && $month > 0 && $month < 13)
	{
		$days_inmonth = (int) date("t", strtotime($year."-".$month."-01"));
	}
	else
		$days_inmonth = 31;

	while ($num <= $days_inmonth)
	{
		// zero-fill
		if ($num < 10) $num = "0$num";
		else $num = "$num";
		$days[$num] = $num;
		$num++;
	}
	return $days;
}

/**
 *	Get calendar months in array format.
 *	@return array $months months from 01-12 (zero-filled)
 */
function array_months()
{
  $months=array(
    '01' => 'Jan',
    '02' => 'Feb',
    '03' => 'Mar',
    '04' => 'Apr',
    '05' => 'May',
    '06' => 'Jun',
    '07' => 'Jul',
    '08' => 'Aug',
    '09' => 'Sep',
    '10' => 'Oct',
    '11' => 'Nov',
    '12' => 'Dec',
  );
  return $months;
}

/**
 *	Get calendar years in array format.
 *	@param int $num number of years to display (optional) default is 5, negative numbers change direction of array
 *	@param int $year starting year (optional) default is this year
 *	@return array $years years
 */
function array_years($num=5,$year='')
{
	$years=Array();
	$year=($year==null)?date('Y'):$year;
	if ($num>0)
	{
		while ($num > 0)
		{
			$years[$year] = $year;
			$year--;
			$num--;
		}
	}
	elseif ($num<0)
	{
		while ($num < 0)
		{
			$years[$year] = $year;
			$year++;
			$num++;
		}
	}
	return $years;
}

/**
 *	Get calendar hours in array format.
 *	@return array $hours hours (zero-filled)
 */
function array_hours()
{
  $hours=array(
    '07' => '7 am',
    '08' => '8 am',
    '09' => '9 am',
    '10' => '10 am',
    '11' => '11 am',
    '12' => '12 pm',
    '13' => '1 pm',
    '14' => '2 pm',
    '15' => '3 pm',
    '16' => '4 pm',
    '17' => '5 pm',
    '18' => '6 pm',
    '19' => '7 pm',
    '20' => '8 pm',
    '21' => '9 pm',
    '22' => '10 pm',
  );
  return $hours;
}

/**
 *	Get array of minutes.
 *	@param int $interval interval between minutes (optional) default is 15
 *	@return array $minutes minutes (zero-filled)
 */
function array_minutes($interval=15)
{
	$minutes=array();
	$count=$interval;
	for ($i=0;$i<60;$i+=$interval)
	{
		$tmp=($i<10)?'0'.$i:$i;
		$minutes[$tmp]=$tmp;
	}
	return $minutes;
}

/**
 *	Get array of states.
 *	@return array $states states (abbr=>fullname)
 */
function array_states()
{
  $states=array (
    'AL' => 'Alabama',
    'AK' => 'Alaska',
    'AS' => 'American Samoa',
    'AZ' => 'Arizona',
    'AR' => 'Arkansas',
    'CA' => 'California',
    'CO' => 'Colorado',
    'CT' => 'Connecticut',
    'DE' => 'Delaware',
    'DC' => 'District of Columbia',
    'FM' => 'Federated States of Micronesia',
    'FL' => 'Florida',
    'GA' => 'Georgia',
    'GU' => 'Guam',
    'HI' => 'Hawaii',
    'ID' => 'Idaho',
    'IL' => 'Illinois',
    'IN' => 'Indiana',
    'IA' => 'Iowa',
    'KS' => 'Kansas',
    'KY' => 'Kentucky',
    'LA' => 'Louisiana',
    'ME' => 'Maine',
    'MH' => 'Marshall Islands',
    'MD' => 'Maryland',
    'MA' => 'Massachusetts',
    'MI' => 'Michigan',
    'MN' => 'Minnesota',
    'MS' => 'Mississippi',
    'MO' => 'Missouri',
    'MT' => 'Montana',
    'NE' => 'Nebraska',
    'NV' => 'Nevada',
    'NH' => 'New Hampshire',
    'NJ' => 'New Jersey',
    'NM' => 'New Mexico',
    'NY' => 'New York',
    'NC' => 'North Carolina',
    'ND' => 'North Dakota',
    'MP' => 'Northern Mariana Islands',
    'OH' => 'Ohio',
    'OK' => 'Oklahoma',
    'OR' => 'Oregon',
    'PW' => 'Palau',
    'PA' => 'Pennsylvania',
    'PR' => 'Puerto Rico',
    'RI' => 'Rhode Island',
    'SC' => 'South Carolina',
    'SD' => 'South Dakota',
    'TN' => 'Tennessee',
    'TX' => 'Texas',
    'UT' => 'Utah',
    'VT' => 'Vermont',
    'VI' => 'Virgin Islands',
    'VA' => 'Virginia',
    'WA' => 'Washington',
    'WV' => 'West Virginia',
    'WI' => 'Wisconsin',
    'WY' => 'Wyoming'
  );
  return $states;
}

/**
 *	Writes the beginning form tag.
 *	@param string $name form name
 *	@param string $class class name
 *	@param string $method method (post or get)
 *	@param string $action action
 */
function form_start($name='form', $class=null, $method='post', $action=null, $extra=null)
{
	$query_string = (empty($_SERVER['QUERY_STRING'])) ? '' : '?'.htmlentities($_SERVER['QUERY_STRING']);
	$action = (empty($action)) ? $_SERVER['PHP_SELF'].$query_string : $action;
	echo "\n";
	echo "<form name=\"$name\" id=\"$name\"";
	echo ($class) ? " class=\"$class\"" : '';
	echo " method=\"$method\" action=\"$action\" $extra>";  
}

/**
 *	Writes the ending form tag.
 */
function form_end()
{
	echo "\n".'</form>';  
}

/**
 *	Writes a form input label.
 *	@param string $text label text
 *	@param string $for id of corresponding field
 *	@param string $class class css class of label
 *	@param string $extra any extra parameters (optional)
 */
function form_label($text=null, $for=null, $class=null, $extra=null)
{
	if ($extra) {$extra = ' '.$extra;}
	echo "\n";
	echo '<label';	
	echo ($for) ? " for=\"$for\"" : '';
	echo ($class) ? " class=\"$class\"" : '';
	echo "$extra>$text</label>";
}

/**
 *	Writes a text input.
 *	@param string $name name of field
 *	@param string $id id of field, must be unique per page
 *	@param string $css css class
 *	@param string $value value
 *	@param int $size size of field
 *	@param int $maxlength maxlength of field
 *	@param string $extra any extra parameters (optional)
 */	
function form_text($name, $id=null, $class=null, $value=null, $size='30', $maxlength='100', $extra=null)
{
	if ($extra) {$extra = ' '.$extra;}
	echo '<input type="text" name="'.$name.'"';
	echo ($id) ? " id=\"$id\"" : '';
	echo ($class) ? " class=\"$class\"" : '';
	echo ($value) ? " value=\"$value\"" : '';	
	echo " size=\"$size\" maxlength=\"$maxlength\"$extra />";
}

/**
 *	Writes a password input.
 *	@param string $name name of field
 *	@param string $id id of field, must be unique per page
 *	@param string $css css class
 *	@param int $size size of field (optional) default is 30
 *	@param int $maxlength maxlength of field (optional)
 *	@param string $extra any extra parameters (optional)
 */	
function form_password($name, $id=null, $class=null, $size='30', $maxlength='100', $extra=null)
{
	if ($extra) {$extra = ' '.$extra; }
	echo "\n";
	echo "<input type=\"password\" name=\"$name\"";
	echo ($id) ? " id=\"$id\"" : '';
	echo ($class) ? " class=\"$class\"" : '';
	echo " size=\"$size\" maxlength=\"$maxlength\"$extra />";
}

/**
 *	Writes a checkbox input.
 *	@param string $name name of field
 *	@param string $id id of field, must be unique per page
 *	@param string $class css class
 *	@param string $value value
 *	@param bool $checked checked?
 *  @param string $extra any extra parameters (optional)
 */
function form_checkbox($name, $id=null, $class=null, $value=null, $checked=0, $extra=null)
{
	if ($extra) {$extra = ' '.$extra;}
	if ($checked == 1)
	{
		echo "\n";
		echo "<input type=\"checkbox\" name=\"$name\"";
		echo ($id) ? " id=\"$id\"" : '';
		echo ($class) ? " class=\"$class\"" : '';
		echo ($value) ? " value=\"$value\"" : '';
		echo " checked=\"checked\"$extra />";  
	}
	else
	{
		echo "\n";
		echo "<input type=\"checkbox\" name=\"$name\"";
		echo ($id) ? " id=\"$id\"" : '';
		echo ($class) ? " class=\"$class\"" : '';
		echo ($value) ? " value=\"$value\"" : '';
		echo "$extra />";  
	}
}

/**
 *	Writes a radio input.
 *	@param string $name name of field
 *	@param string $id id of field, must be unique per page
 *	@param string $class css class
 *	@param string $value value
 *	@param bool $checked checked?
 *  @param string $extra any extra parameters (optional)
 */
function form_radio($name, $id=null, $class=null, $value=null, $checked=0, $extra=null)
{
	if ($extra) { $extra = ' '.$extra; }
	if ($checked == 1)
	{
		echo "\n";
		echo "<input type=\"radio\" name=\"$name\"";
		echo ($id) ? " id=\"$id\"" : '';
		echo ($class) ? " class=\"$class\"" : '';
		echo ($value) ? " value=\"$value\"" : '';
		echo " checked=\"checked\"$extra />";  
	}
	else
	{
		echo "\n";
		echo "<input type=\"radio\" name=\"$name\"";
		echo ($id) ? " id=\"$id\"" : '';
		echo ($class) ? " class=\"$class\"" : '';
		echo ($value) ? " value=\"$value\"" : '';
		echo "$extra />";  
	}
}

/**
 *	Writes a submit input.
 *  @param string $id the id attribute
 *	@param string $name name name of field
 *	@param string $class css class
 *	@param string $value value (button text)
 *  @param string $extra any extra parameters (optional)
 */
function form_submit($name, $id=null, $class=null, $value='Submit', $extra=null)
{
	if ($extra) {$extra = ' '.$extra;}
	echo "\n";
	echo "<input type=\"submit\" name=\"$name\"";
	echo ($id) ? " id=\"$id\"" : '';
	echo ($class) ? " class=\"$class\"" : '';
	echo " value=\"$value\"$extra />";
}

/**
 *	Writes a reset input.
 *	@param string $name name of field
 *	@param string $class css class
 *	@param string $value value (button text)
 *  @param string $extra any extra parameters (optional)
 */
function form_reset($name, $class=null, $value='Reset', $extra=null)
{
	if ($extra) {$extra = ' '.$extra;}
	echo "\n";
	echo "<input type=\"reset\" name=\"$name\" id=\"$name\"";
	echo ($class) ? " class=\"$class\"" : '';
	echo " value=\"$value\"$extra />";
}

/**
 *	Writes a hidden field.
 *	@param string $name name of field
 *	@param string $value value
 *  @param string $extra any extra parameters (optional)
 */
function form_hidden($name, $value=null, $extra=null)
{
	if ($extra) {$extra = ' '.$extra;}
	echo "\n";
	echo "<input type=\"hidden\" name=\"$name\"";
	echo ($value) ? " value=\"$value\"" : '';
	echo "$extra />"; 
}

/**
 *	Writes a select list with options.
 *	@param string $name name of field
 *	@param string $id id of field, must be unique per page
 *	@param string $class css class
 *	@param array $options possible options, usually pulled from db, or array_* funcs
 *	@param string $selected if the value matches, it is selected
 *
 *	Multiple selects based on sets come out of a database as val,val,val
 *	so the explode was intended to create the instance of an array based 
 *	on the string regardless of whether or not it has val,val,val.
 *		
 *  @param string $extra any extra parameters (optional)
 */
function form_select($name, $id=null, $class=null, $options=null, $selected=null, $extra=null)
{
	if ($extra) {$extra = ' '.$extra;}
	if (!empty($selected))
	{
		$selected = explode(',',$selected);
		foreach ($selected as $key=>$val) {$selected[$key]=trim($val);}
	}
	echo "\n";
	echo "<select name=\"$name\"";
	echo ($id) ? " id=\"$id\"" : '';
	echo ($class) ? " class=\"$class\"" : '';
	echo "$extra>";
	if (is_array($options))
	{
		foreach ($options as $key=>$val)
		{
			if (!empty($selected) && in_array($key, $selected))
				echo "\n\t".'<option value="'.$key.'" selected="selected">'.$val.'</option>';
			else
				echo "\n\t".'<option value="'.$key.'">'.$val.'</option>';
		}
	}
	echo "\n".'</select>';
}

/**
 *	Writes a textarea
 *	@param string $name name of field
 *	@param string $id id of field, must be unique per page
 *	@param string $class css class
 *	@param int $rows number of rows (height)
 *	@param int $cols number of cols (width)
 *	@param string $value value of field
 *	@param string $extra any extra parameters
 */
function form_textarea($name, $id=null, $class=null, $rows='6', $cols='50', $value=null, $extra=null)
{
	if ($extra) {$extra = ' '.$extra;}
	echo "\n";
	echo "<textarea name=\"$name\"";
	echo ($id) ? " id=\"$id\"" : '';
	echo ($class) ? " class=\"$class\"" : '';
	echo " rows=\"$rows\" cols=\"$cols\"";
	echo "$extra>$value</textarea>";
}

/**
 *	Fix dates for form display, or proper db entry
 *	@param array $dates array of date field names
 * 	@param array $datetimes array of datetime field names
 *	@param int $way 1 is done after a post, 2 is done when selecting for forms
 *	@param array $orig for way 2, the array we need to add the separated date values to (usually $posts)
 *	@return mixed null, or the original array modified to have separated date values for the forms
 */
function form_array_fix_dates($dates,$datetimes,$way=1,$orig='')
{
    if($way==1)
    {
		if (is_array($dates))
		{
			foreach ($dates as $date)
			{
				$_POST[$date]=form_array_get_date($date);
			}
		}
		if (is_array($datetimes))
		{
			foreach ($datetimes as $datetime)
			{
				$_POST[$datetime]=form_array_get_datetime($datetime);
			}
		}
    }
    elseif ($way==2)
    {
		if (is_array($dates))
		{
			foreach ($dates as $date)
			{
				list(${date.'_year'},${date.'_month'},${date.'_day'})=explode('-',$orig[$date]);
				$orig[$date.'_year']=${date.'_year'};
				$orig[$date.'_month']=${date.'_month'};
				$orig[$date.'_day']=${date.'_day'};
			}
		}
		if (is_array($datetimes))
		{
			foreach ($datetimes as $datetime)
			{
				$buf=explode(' ',$orig[$datetime]);
				$date=explode('-',$buf[0]);
				$time=explode(':',$buf[1]);
				$orig[$datetime.'_year']=$date[0];
				$orig[$datetime.'_month']=$date[1];
				$orig[$datetime.'_day']=$date[2];
				$orig[$datetime.'_hour']=$time[0];
				$orig[$datetime.'_minute']=$time[1];
			}
		}
        return $orig;
    }
}

/**
 *	Get put a date back together after a POST.
 *	@param string $field name of post index of date field
 *	@param int $key index of form array that the field value belongs to
 * 	@return array $date repaired date, as an array that corresponds to the form
 */
function form_array_get_date($field)
{
	$keys=array_keys($_POST[$field.'_year']);
	foreach ($keys as $key)
	{
		$date[$key]=$_POST[$field.'_year'][$key].'-'.$_POST[$field.'_month'][$key].'-'.$_POST[$field.'_day'][$key];
	}
	return $date;
}

/**
 *	Get put a datetime back together after a POST.
 *	@param string $field name of post index of datetime field
 *	@param int $key index of form array that the field value belongs to
 * 	@return array $datetime repaired datetime, as an array that corresponds to the form
 */
function form_array_get_datetime($field)
{
	$keys=array_keys($_POST[$field.'_year']);
	foreach ($keys as $key)
	{
		$datetime[$key]=$_POST[$field.'_year'][$key].'-'.$_POST[$field.'_month'][$key].'-'.$_POST[$field.'_day'][$key].' '.$_POST[$field.'_hour'][$key].':'.$_POST[$field.'_minute'][$key];
	}
	return $datetime;
}

/**
 *	Validates email addresses
 *	@param string $email
 *	@returns bool
 */
function is_email_address($email)
{
  return preg_match("/^ *[0-9a-zA-Z]+[-_\.0-9a-zA-Z]*@([0-9a-zA-Z]+[-\.0-9a-zA-Z]+)+\.[a-zA-Z]+ *$/", $email);
}

/**
 *	Validates phone number
 *	@param string $phone
 *	@returns bool
 */
function is_phone_number($phone)
{
	return preg_match("/^ *((1[- \.]?((\([0-9]{3}\))|([0-9]{3}))[- \.]?)|((((\([0-9]{3}\))|([0-9]{3}))[- \.]?)?))[0-9]{3}[- \.]?[0-9]{4} *$/", $phone);
}

/**
 *	Returns http:// and the string if the string does not begin with http://
 *	@param string $url
 *	@returns string
 */
function url_out($url)
{
  return (preg_match("#^http://#", $url)) ? trim($url) : 'http://'.trim($url);
}

/**
 *	Take a db_get result and return an array of options.
 *	@param array $data db_get result
 *	@param string $val_col column containing the value for each option
 *	@param string $name_col column containing the text
 *	@return array $options array of options ($val=>$text)
 */
function db_get_to_options($data,$val_col,$name_col)
{
	$options=array();
	foreach ($data as $row)
	{
		$options[$row[$val_col]]=$row[$name_col];
	}
	return $options;
}
?>
